const USERS_KEY = "bingo_users";
const BOARDS_KEY = "bingo_boards";
const CURRENT_USER_KEY = "bingo_current_user";

const BINGO_WORDS = [
  "Deploy day",
  "Bug fix",
  "Pair programming",
  "Coffee break",
  "Code review",
  "Ship it",
  "Hotfix",
  "Stand-up",
  "Retrospective",
  "Sprint planning",
  "Merge conflict",
  "Refactor",
  "Unit tests",
  "Integration tests",
  "Design doc",
  "Customer feedback",
  "Performance win",
  "Feature flag",
  "Launch checklist",
  "On-call",
  "Incident report",
  "Status update",
  "Slack ping",
  "Build failure",
  "Lint warning",
  "Tech debt",
  "Dependency update",
  "Roadmap",
  "Demo day",
  "Documentation",
  "Code freeze",
  "UX review",
  "Stakeholder sync",
  "Bug bash",
  "Release notes",
  "User story",
  "Priority shift",
  "Scope change",
  "New hire",
  "Hackathon",
  "Brainstorm",
  "Benchmark",
  "Accessibility",
  "Security review",
  "Data migration",
  "Telemetry",
  "Cache miss",
  "Load test",
  "Timeout",
  "Regression",
  "All hands",
];

function readJson(key, fallback) {
  const raw = localStorage.getItem(key);
  if (!raw) {
    return fallback;
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    return fallback;
  }
}

function writeJson(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function normalizeUsername(username) {
  return username.trim().toLowerCase();
}

function validateUsername(username) {
  if (username.length < 3) {
    throw new Error("Username must be at least 3 characters.");
  }
}

function validatePassword(password, minLength = 6) {
  if (password.length < minLength) {
    throw new Error(`Password must be at least ${minLength} characters.`);
  }
}

async function hashPassword(password) {
  const encoder = new TextEncoder();
  const data = encoder.encode(password);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

function getUsers() {
  return readJson(USERS_KEY, {});
}

function saveUsers(users) {
  writeJson(USERS_KEY, users);
}

function getBoards() {
  return readJson(BOARDS_KEY, {});
}

function saveBoards(boards) {
  writeJson(BOARDS_KEY, boards);
}

export function getCurrentUser() {
  return localStorage.getItem(CURRENT_USER_KEY);
}

function setCurrentUser(username) {
  localStorage.setItem(CURRENT_USER_KEY, username);
}

export function logoutUser() {
  localStorage.removeItem(CURRENT_USER_KEY);
}

export async function registerUser(username, password) {
  const normalized = normalizeUsername(username);
  validateUsername(normalized);
  validatePassword(password, 6);

  const users = getUsers();
  if (users[normalized]) {
    throw new Error("That username is already registered.");
  }
  const passwordHash = await hashPassword(password);
  users[normalized] = {
    username: normalized,
    passwordHash,
    createdAt: new Date().toISOString(),
  };
  saveUsers(users);
  setCurrentUser(normalized);
  ensureBoard(normalized);
  return normalized;
}

export async function loginUser(username, password) {
  const normalized = normalizeUsername(username);
  validateUsername(normalized);
  validatePassword(password, 1);

  const users = getUsers();
  const user = users[normalized];
  if (!user) {
    throw new Error("Unknown username. Please register first.");
  }
  const passwordHash = await hashPassword(password);
  if (user.passwordHash !== passwordHash) {
    throw new Error("Invalid password.");
  }
  setCurrentUser(normalized);
  ensureBoard(normalized);
  return normalized;
}

function createBoard() {
  const pool = [...BINGO_WORDS];
  if (pool.length < 24) {
    throw new Error("Not enough words to build a bingo board.");
  }
  const cells = [];
  for (let index = 0; index < 25; index += 1) {
    if (index === 12) {
      cells.push({ text: "FREE", marked: true });
    } else {
      const choiceIndex = Math.floor(Math.random() * pool.length);
      const [choice] = pool.splice(choiceIndex, 1);
      cells.push({ text: choice, marked: false });
    }
  }
  return {
    size: 5,
    cells,
    updatedAt: new Date().toISOString(),
  };
}

function ensureBoard(username) {
  const boards = getBoards();
  if (boards[username]) {
    return boards[username];
  }
  const board = createBoard();
  boards[username] = board;
  saveBoards(boards);
  return board;
}

export function getBoard(username) {
  return ensureBoard(username);
}

export function saveBoard(username, board) {
  const boards = getBoards();
  boards[username] = {
    ...board,
    updatedAt: new Date().toISOString(),
  };
  saveBoards(boards);
}

export function resetBoard(username) {
  const boards = getBoards();
  const board = createBoard();
  boards[username] = board;
  saveBoards(boards);
  return board;
}
