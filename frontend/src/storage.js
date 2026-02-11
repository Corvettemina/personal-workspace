const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";
const TOKEN_KEY = "auth_token";
const USER_KEY = "auth_user";

// Helper functions for API calls
async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY);
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || `Request failed: ${response.statusText}`);
  }

  return data;
}

// Store token and user info
function setAuth(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

// Clear auth data
function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

// Get current user from storage
export function getCurrentUser() {
  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) {
    return null;
  }
  try {
    const user = JSON.parse(userStr);
    return user.username || null;
  } catch {
    return null;
  }
}

// Get full user object
export function getCurrentUserData() {
  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) {
    return null;
  }
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

// Logout user
export function logoutUser() {
  clearAuth();
}

// Register new user
export async function registerUser(username, password) {
  if (!username || !password) {
    throw new Error("Username and password are required.");
  }

  if (username.length < 3) {
    throw new Error("Username must be at least 3 characters.");
  }

  if (password.length < 6) {
    throw new Error("Password must be at least 6 characters.");
  }

  try {
    const data = await apiRequest("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        username,
        password,
      }),
    });

    setAuth(data.access_token, data.user);
    return data.user.username;
  } catch (error) {
    throw error;
  }
}

// Login user
export async function loginUser(username, password) {
  if (!username || !password) {
    throw new Error("Username and password are required.");
  }

  try {
    const data = await apiRequest("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        username,
        password,
      }),
    });

    setAuth(data.access_token, data.user);
    return data.user.username;
  } catch (error) {
    throw error;
  }
}

// Verify current token and get user info
export async function verifyAuth() {
  try {
    const data = await apiRequest("/auth/me");
    setAuth(localStorage.getItem(TOKEN_KEY), data.user);
    return data.user;
  } catch (error) {
    clearAuth();
    return null;
  }
}

// Bingo board functions (keeping local storage for board data for now)
// You can later migrate these to the backend if needed
const BOARDS_KEY = "bingo_boards";

// Helper to clear all boards (useful for debugging)
export function clearAllBoards() {
  localStorage.removeItem(BOARDS_KEY);
}

const BINGO_WORDS = [
  "Faris says 'Faris'",
  "JL and Fawzy beef",
  "Mark Burps",
  "John I. says he's horny",
  "Rat says 'I'm not drunk'",
  "Tony T throws up for no reason",
  "Alex flakes on the whole trip",
  "Someone loses their phone",
  "Stripper shows up unexpectedly",
  "Someone passes out early",
  "Someone gets lost",
  "Someone calls their girlfriend",
  "Drunk dialing incident",
  "Someone loses wallet",
  "Someone pukes in Uber",
  "Strip club debate",
  "Someone gets kicked out",
  "Mark gets too drunk",
  "Someone breaks something",
  "Late night food run",
  "Someone falls asleep standing",
  "Group chat spam",
  "Someone forgets where hotel is",
  "Someone tries to fight a bouncer",
  "Mark gets emotional",
  "Youssef Pees all over the bathroom",
  "Someone hits on the waitress",
  "Someone falls off barstool",
  "Someone loses their keys",
  "Someone tries to start a fight",
  "Someone gets kicked out of club",
  "Someone passes out in bathroom",
  "Someone tries to drive drunk",
  "Someone loses their shirt",
  "Someone gets a tattoo",
  "Someone tries to fight",
  "Someone gets thrown in pool",
  "Someone orders way too much food",
  "Someone falls down stairs",
  "Someone gets locked out of room",
];

function hashStringToSeed(value) {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function mulberry32(seed) {
  let state = seed >>> 0;
  return function random() {
    state += 0x6d2b79f5;
    let result = Math.imul(state ^ (state >>> 15), state | 1);
    result ^= result + Math.imul(result ^ (result >>> 7), result | 61);
    return ((result ^ (result >>> 14)) >>> 0) / 4294967296;
  };
}

function shuffleArray(items, rng = Math.random) {
  const array = [...items];
  for (let index = array.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(rng() * (index + 1));
    [array[index], array[swapIndex]] = [array[swapIndex], array[index]];
  }
  return array;
}

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

function getBoards() {
  return readJson(BOARDS_KEY, {});
}

function saveBoards(boards) {
  writeJson(BOARDS_KEY, boards);
}

function createBoard(username) {
  if (!username) {
    throw new Error("Username is required to build a board.");
  }
  if (BINGO_WORDS.length < 24) {
    throw new Error("Not enough words to build a bingo board.");
  }
  const seed = hashStringToSeed(`bingo:${username}`);
  const rng = mulberry32(seed);
  const pool = shuffleArray(BINGO_WORDS, rng).slice(0, 24);
  const cells = [];
  let wordIndex = 0;
  for (let index = 0; index < 25; index += 1) {
    if (index === 12) {
      cells.push({ text: "FREE", marked: true });
    } else {
      cells.push({ text: pool[wordIndex], marked: false });
      wordIndex += 1;
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
  const board = createBoard(username);
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
  const existing = boards[username];
  if (existing?.cells?.length === 25) {
    const next = {
      ...existing,
      cells: existing.cells.map((cell, index) => ({
        ...cell,
        marked: index === 12 ? true : false,
      })),
      updatedAt: new Date().toISOString(),
    };
    boards[username] = next;
    saveBoards(boards);
    return next;
  }
  const board = createBoard(username);
  boards[username] = board;
  saveBoards(boards);
  return board;
}

export function regenerateBoard(username) {
  /**Create a completely new board with new words from BINGO_WORDS*/
  console.log("regenerateBoard called with username:", username);
  
  if (!username) {
    throw new Error("Username is required to build a board.");
  }
  if (BINGO_WORDS.length < 24) {
    throw new Error(`Not enough words to build a bingo board. Need 24, have ${BINGO_WORDS.length}`);
  }
  
  // Use timestamp + username for a unique seed each time
  const seed = hashStringToSeed(`bingo:${username}:${Date.now()}`);
  const rng = mulberry32(seed);
  const pool = shuffleArray([...BINGO_WORDS], rng).slice(0, 24);
  const cells = [];
  let wordIndex = 0;
  for (let index = 0; index < 25; index += 1) {
    if (index === 12) {
      cells.push({ text: "FREE", marked: true });
    } else {
      cells.push({ text: pool[wordIndex], marked: false });
      wordIndex += 1;
    }
  }
  
  const board = {
    size: 5,
    cells,
    updatedAt: new Date().toISOString(),
  };
  
  console.log("New board created with cells:", cells.map(c => c.text));
  
  const boards = getBoards();
  boards[username] = board;
  saveBoards(boards);
  return board;
}
