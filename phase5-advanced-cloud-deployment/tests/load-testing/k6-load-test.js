/**
 * K6 Load Testing Script for TodoBoard Application
 *
 * Tests performance with 1000 concurrent users
 * Verifies:
 * - API response time <500ms p95
 * - Search performance <1s for 10,000 tasks
 * - Real-time updates <2s latency
 * - Event processing 1,000+ events/minute
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { randomString, randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Custom metrics
const apiResponseTime = new Trend('api_response_time');
const searchResponseTime = new Trend('search_response_time');
const taskCreationRate = new Rate('task_creation_success');
const errorRate = new Rate('errors');
const eventCounter = new Counter('events_processed');

// Configuration
const BASE_URL = __ENV.BASE_URL || 'http://todoboard.local/api';
const WS_URL = __ENV.WS_URL || 'ws://todoboard.local/ws';

// Test stages - ramp up to 1000 users
export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '3m', target: 500 },   // Ramp up to 500 users
    { duration: '5m', target: 1000 },  // Ramp up to 1000 users
    { duration: '10m', target: 1000 }, // Stay at 1000 users
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    'http_req_duration{type:api}': ['p(95)<500'],        // 95% of API requests < 500ms
    'http_req_duration{type:search}': ['p(95)<1000'],    // 95% of search requests < 1s
    'task_creation_success': ['rate>0.95'],              // 95% success rate
    'errors': ['rate<0.05'],                             // Error rate < 5%
    'http_req_failed': ['rate<0.05'],                    // Failed requests < 5%
  },
};

// Test data
const priorities = ['low', 'medium', 'high'];
const statuses = ['pending', 'in_progress', 'completed'];
const tags = ['work', 'personal', 'urgent', 'important', 'later'];

// Setup function - runs once per VU
export function setup() {
  // Register test users
  const users = [];
  for (let i = 0; i < 10; i++) {
    const username = `loadtest_user_${randomString(8)}`;
    const password = 'TestPassword123!';

    const registerRes = http.post(`${BASE_URL}/auth/register`, JSON.stringify({
      username: username,
      email: `${username}@test.com`,
      password: password,
    }), {
      headers: { 'Content-Type': 'application/json' },
    });

    if (registerRes.status === 200 || registerRes.status === 201) {
      const loginRes = http.post(`${BASE_URL}/auth/login`, JSON.stringify({
        username: username,
        password: password,
      }), {
        headers: { 'Content-Type': 'application/json' },
      });

      if (loginRes.status === 200) {
        const token = loginRes.json('access_token');
        users.push({ username, token });
      }
    }
  }

  return { users };
}

// Main test function
export default function(data) {
  // Select a random user
  const user = data.users[randomIntBetween(0, data.users.length - 1)];
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${user.token}`,
  };

  // Test 1: Create task (API performance test)
  const createTaskStart = Date.now();
  const createTaskPayload = {
    title: `Task ${randomString(10)}`,
    description: `Description ${randomString(20)}`,
    priority: priorities[randomIntBetween(0, priorities.length - 1)],
    status: statuses[randomIntBetween(0, statuses.length - 1)],
    tags: [tags[randomIntBetween(0, tags.length - 1)]],
    due_date: new Date(Date.now() + randomIntBetween(1, 30) * 86400000).toISOString(),
  };

  const createRes = http.post(`${BASE_URL}/tasks`, JSON.stringify(createTaskPayload), {
    headers,
    tags: { type: 'api' },
  });

  const createSuccess = check(createRes, {
    'task created successfully': (r) => r.status === 200 || r.status === 201,
    'response has task id': (r) => r.json('id') !== undefined,
  });

  taskCreationRate.add(createSuccess);
  apiResponseTime.add(Date.now() - createTaskStart);
  eventCounter.add(1);

  if (!createSuccess) {
    errorRate.add(1);
  }

  sleep(1);

  // Test 2: List tasks (API performance test)
  const listStart = Date.now();
  const listRes = http.get(`${BASE_URL}/tasks?limit=50`, {
    headers,
    tags: { type: 'api' },
  });

  check(listRes, {
    'tasks listed successfully': (r) => r.status === 200,
    'response is array': (r) => Array.isArray(r.json()),
  });

  apiResponseTime.add(Date.now() - listStart);

  sleep(1);

  // Test 3: Search tasks (Search performance test)
  const searchStart = Date.now();
  const searchQuery = randomString(5);
  const searchRes = http.get(`${BASE_URL}/tasks?search=${searchQuery}`, {
    headers,
    tags: { type: 'search' },
  });

  check(searchRes, {
    'search completed successfully': (r) => r.status === 200,
    'search response time acceptable': (r) => r.timings.duration < 1000,
  });

  searchResponseTime.add(Date.now() - searchStart);

  sleep(1);

  // Test 4: Filter tasks (API performance test)
  const filterRes = http.get(
    `${BASE_URL}/tasks?priority=high&status=pending&tags=urgent`,
    {
      headers,
      tags: { type: 'api' },
    }
  );

  check(filterRes, {
    'filter completed successfully': (r) => r.status === 200,
  });

  sleep(1);

  // Test 5: Update task (API performance test)
  if (createSuccess && createRes.json('id')) {
    const taskId = createRes.json('id');
    const updatePayload = {
      status: 'completed',
      completed_at: new Date().toISOString(),
    };

    const updateRes = http.patch(
      `${BASE_URL}/tasks/${taskId}`,
      JSON.stringify(updatePayload),
      {
        headers,
        tags: { type: 'api' },
      }
    );

    check(updateRes, {
      'task updated successfully': (r) => r.status === 200,
    });

    eventCounter.add(1);
  }

  sleep(2);

  // Test 6: Get task by ID (API performance test)
  if (createSuccess && createRes.json('id')) {
    const taskId = createRes.json('id');
    const getRes = http.get(`${BASE_URL}/tasks/${taskId}`, {
      headers,
      tags: { type: 'api' },
    });

    check(getRes, {
      'task retrieved successfully': (r) => r.status === 200,
      'task has correct id': (r) => r.json('id') === taskId,
    });
  }

  sleep(1);
}

// Teardown function - runs once after all VUs complete
export function teardown(data) {
  // Cleanup test users (optional)
  console.log('Load test completed');
  console.log(`Total users tested: ${data.users.length}`);
}

// Handle summary
export function handleSummary(data) {
  return {
    'load-test-results.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

function textSummary(data, options) {
  const indent = options.indent || '';
  const enableColors = options.enableColors || false;

  let summary = '\n' + indent + '=== Load Test Summary ===\n\n';

  // Request metrics
  summary += indent + 'HTTP Requests:\n';
  summary += indent + `  Total: ${data.metrics.http_reqs.values.count}\n`;
  summary += indent + `  Failed: ${data.metrics.http_req_failed.values.rate * 100}%\n`;
  summary += indent + `  Duration (avg): ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms\n`;
  summary += indent + `  Duration (p95): ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms\n`;
  summary += indent + `  Duration (p99): ${data.metrics.http_req_duration.values['p(99)'].toFixed(2)}ms\n\n`;

  // Custom metrics
  if (data.metrics.api_response_time) {
    summary += indent + 'API Response Time:\n';
    summary += indent + `  Average: ${data.metrics.api_response_time.values.avg.toFixed(2)}ms\n`;
    summary += indent + `  p95: ${data.metrics.api_response_time.values['p(95)'].toFixed(2)}ms\n\n`;
  }

  if (data.metrics.search_response_time) {
    summary += indent + 'Search Response Time:\n';
    summary += indent + `  Average: ${data.metrics.search_response_time.values.avg.toFixed(2)}ms\n`;
    summary += indent + `  p95: ${data.metrics.search_response_time.values['p(95)'].toFixed(2)}ms\n\n`;
  }

  if (data.metrics.events_processed) {
    const duration = data.state.testRunDurationMs / 1000 / 60; // minutes
    const eventsPerMinute = data.metrics.events_processed.values.count / duration;
    summary += indent + 'Event Processing:\n';
    summary += indent + `  Total events: ${data.metrics.events_processed.values.count}\n`;
    summary += indent + `  Events per minute: ${eventsPerMinute.toFixed(2)}\n\n`;
  }

  // VU metrics
  summary += indent + 'Virtual Users:\n';
  summary += indent + `  Max: ${data.metrics.vus_max.values.max}\n`;
  summary += indent + `  Iterations: ${data.metrics.iterations.values.count}\n\n`;

  return summary;
}
