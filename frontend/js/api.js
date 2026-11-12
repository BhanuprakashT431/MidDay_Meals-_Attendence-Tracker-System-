/**
 * API Client & Network Resilience Layer
 * Manages JWT tokens, backend REST calls, offline request queuing,
 * and automatic synchronization for low-connectivity 2G/3G school environments.
 */

const API_BASE = window.location.origin;

class MidDayMealAPI {
  constructor() {
    this.token = localStorage.getItem("auth_token") || null;
    this.currentUser = JSON.parse(localStorage.getItem("user_profile") || "null");
    this.isOnline = navigator.onLine;

    window.addEventListener("online", () => this.handleNetworkChange(true));
    window.addEventListener("offline", () => this.handleNetworkChange(false));
  }

  setSession(token, user) {
    this.token = token;
    this.currentUser = user;
    localStorage.setItem("auth_token", token);
    localStorage.setItem("user_profile", JSON.stringify(user));
  }

  clearSession() {
    this.token = null;
    this.currentUser = null;
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user_profile");
  }

  isAuthenticated() {
    return !!this.token;
  }

  getAuthHeaders() {
    const headers = { "Content-Type": "application/json" };
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const defaultHeaders = this.getAuthHeaders();
    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {})
      }
    };

    try {
      const response = await fetch(url, config);

      if (response.status === 401) {
        // Token expired or invalid
        this.clearSession();
        window.dispatchEvent(new CustomEvent("auth:unauthorized"));
        throw new Error("Session expired. Please log in again.");
      }

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.message || `Request failed with status ${response.status}`);
      }
      return data;
    } catch (error) {
      // If network failure and this was a data mutation, queue offline
      if (!navigator.onLine && options.method && options.method !== "GET" && options.offlineQueueable) {
        this.queueOfflineAction(endpoint, options);
        return {
          offline_queued: true,
          message: window.i18n.t("alert_offline")
        };
      }
      throw error;
    }
  }

  // --- Offline Queue Support ---
  queueOfflineAction(endpoint, options) {
    const queue = JSON.parse(localStorage.getItem("offline_sync_queue") || "[]");
    queue.push({
      id: Date.now(),
      endpoint,
      method: options.method,
      body: options.body,
      timestamp: new Date().toISOString()
    });
    localStorage.setItem("offline_sync_queue", JSON.stringify(queue));
    this.updateOfflineBadge();
  }

  async flushOfflineQueue() {
    const queue = JSON.parse(localStorage.getItem("offline_sync_queue") || "[]");
    if (queue.length === 0) return;

    const remaining = [];
    for (const item of queue) {
      try {
        await this.request(item.endpoint, {
          method: item.method,
          body: item.body
        });
      } catch (e) {
        remaining.push(item);
      }
    }

    localStorage.setItem("offline_sync_queue", JSON.stringify(remaining));
    this.updateOfflineBadge();
    if (remaining.length === 0) {
      window.dispatchEvent(new CustomEvent("toast:show", {
        detail: { message: window.i18n.t("alert_online"), type: "success" }
      }));
    }
  }

  handleNetworkChange(isOnline) {
    this.isOnline = isOnline;
    this.updateOfflineBadge();
    if (isOnline) {
      this.flushOfflineQueue();
    }
  }

  updateOfflineBadge() {
    const badge = document.getElementById("networkStatusBadge");
    const queue = JSON.parse(localStorage.getItem("offline_sync_queue") || "[]");
    if (badge) {
      if (navigator.onLine) {
        badge.className = "network-badge online";
        badge.innerHTML = `<span class="dot"></span> ${window.i18n.t("online_badge")} ${queue.length > 0 ? `(${queue.length} pending sync)` : ""}`;
      } else {
        badge.className = "network-badge offline";
        badge.innerHTML = `<span class="dot"></span> ${window.i18n.t("offline_badge")} (${queue.length} saved)`;
      }
    }
  }

  // --- Auth API ---
  async loginPassword(email, password) {
    const data = await this.request("/api/auth/login-password", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
    this.setSession(data.access_token, data.user);
    return data;
  }

  async requestOTP(email) {
    return await this.request("/api/auth/request-otp", {
      method: "POST",
      body: JSON.stringify({ email })
    });
  }

  async verifyOTP(email, otp) {
    const data = await this.request("/api/auth/verify-otp", {
      method: "POST",
      body: JSON.stringify({ email, otp })
    });
    this.setSession(data.access_token, data.user);
    return data;
  }

  async registerUser(userData) {
    const data = await this.request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(userData)
    });
    this.setSession(data.access_token, data.user);
    return data;
  }

  // --- Dashboard API ---
  async getDashboardSummary(dateStr = null) {
    const url = dateStr ? `/api/dashboard/summary?target_date=${dateStr}` : "/api/dashboard/summary";
    return await this.request(url);
  }

  // --- Attendance API ---
  async getClasses() {
    return await this.request("/api/classes");
  }

  async getAttendance(dateStr = null) {
    const url = dateStr ? `/api/attendance/records?date_str=${dateStr}` : "/api/attendance/records";
    return await this.request(url);
  }

  async submitAttendance(date, items) {
    return await this.request("/api/attendance/submit", {
      method: "POST",
      body: JSON.stringify({ date, items }),
      offlineQueueable: true
    });
  }

  // --- Meals API ---
  async submitMealLog(mealData) {
    return await this.request("/api/meals/submit", {
      method: "POST",
      body: JSON.stringify(mealData),
      offlineQueueable: true
    });
  }

  async getMealHistory(limit = 30) {
    return await this.request(`/api/meals/history?limit=${limit}`);
  }

  // --- Inventory & Produce API ---
  async getInventoryItems() {
    return await this.request("/api/inventory/items");
  }

  async addStockInward(inwardData) {
    return await this.request("/api/inventory/inward", {
      method: "POST",
      body: JSON.stringify(inwardData)
    });
  }

  async addFreshProduce(produceData) {
    return await this.request("/api/inventory/fresh-produce", {
      method: "POST",
      body: JSON.stringify(produceData)
    });
  }

  async getTransactions(limit = 50) {
    return await this.request(`/api/inventory/transactions?limit=${limit}`);
  }

  // --- Reports & Audit ---
  async getMonthlyReport(yearMonth = null) {
    const url = yearMonth ? `/api/reports/monthly?year_month=${yearMonth}` : "/api/reports/monthly";
    return await this.request(url);
  }

  async getAuditLogs(limit = 50) {
    return await this.request(`/api/audit/logs?limit=${limit}`);
  }

  // --- Integrations & Keys ---
  async getPublicConfig() {
    return await this.request("/api/config/public");
  }

  async updateRuntimeKeys(payload) {
    return await this.request("/api/config/update-keys", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }
}

// Global API instance
window.api = new MidDayMealAPI();
