import { useEffect, useMemo, useState } from "react";
import {
  getBoard,
  getCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
  resetBoard,
  saveBoard,
} from "./storage";

const EMPTY_FORM = { username: "", password: "" };

function checkBingo(cells) {
  if (!cells || cells.length !== 25) {
    return false;
  }
  const size = 5;
  const isMarked = (row, col) => cells[row * size + col].marked;

  for (let row = 0; row < size; row += 1) {
    let rowComplete = true;
    for (let col = 0; col < size; col += 1) {
      rowComplete = rowComplete && isMarked(row, col);
    }
    if (rowComplete) {
      return true;
    }
  }

  for (let col = 0; col < size; col += 1) {
    let colComplete = true;
    for (let row = 0; row < size; row += 1) {
      colComplete = colComplete && isMarked(row, col);
    }
    if (colComplete) {
      return true;
    }
  }

  let diagDown = true;
  let diagUp = true;
  for (let index = 0; index < size; index += 1) {
    diagDown = diagDown && isMarked(index, index);
    diagUp = diagUp && isMarked(index, size - index - 1);
  }
  return diagDown || diagUp;
}

function App() {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState(EMPTY_FORM);
  const [user, setUser] = useState(null);
  const [board, setBoard] = useState(null);
  const [view, setView] = useState("board");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const current = getCurrentUser();
    if (current) {
      setUser(current);
      setBoard(getBoard(current));
      setView("board");
    }
  }, []);

  const markedCount = useMemo(() => {
    if (!board) {
      return 0;
    }
    return board.cells.filter((cell) => cell.marked).length;
  }, [board]);

  const hasBingo = useMemo(() => (board ? checkBingo(board.cells) : false), [board]);

  const lastUpdated = useMemo(() => {
    if (!board?.updatedAt) {
      return "Not yet";
    }
    return new Date(board.updatedAt).toLocaleString();
  }, [board]);

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "login") {
        await loginUser(form.username, form.password);
      } else {
        await registerUser(form.username, form.password);
      }
      const current = getCurrentUser();
      setUser(current);
      setBoard(getBoard(current));
      setView("board");
      setForm(EMPTY_FORM);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logoutUser();
    setUser(null);
    setBoard(null);
    setForm(EMPTY_FORM);
    setMode("login");
    setView("board");
    setError("");
  };

  const handleToggle = (index) => {
    if (!board || !user) {
      return;
    }
    if (index === 12) {
      return;
    }
    setBoard((prev) => {
      const updatedAt = new Date().toISOString();
      const next = {
        ...prev,
        updatedAt,
        cells: prev.cells.map((cell, idx) =>
          idx === index ? { ...cell, marked: !cell.marked } : cell,
        ),
      };
      saveBoard(user, next);
      return next;
    });
  };

  const handleReset = () => {
    if (!user) {
      return;
    }
    const confirmed = window.confirm("Reset your marks and keep this board?");
    if (!confirmed) {
      return;
    }
    const next = resetBoard(user);
    setBoard(next);
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Bingo Board</h1>
          <p className="subtitle">Play, mark, and track your progress locally.</p>
        </div>
        {user ? (
          <div className="user-info">
            <span className="user-pill">Signed in as {user}</span>
            <button className="secondary" type="button" onClick={handleLogout}>
              Log out
            </button>
          </div>
        ) : null}
      </header>

      <main className="content">
        {!user ? (
          <section className="card auth-card">
            <div className="tab-bar">
              <button
                type="button"
                className={mode === "login" ? "active" : ""}
                onClick={() => setMode("login")}
              >
                Login
              </button>
              <button
                type="button"
                className={mode === "register" ? "active" : ""}
                onClick={() => setMode("register")}
              >
                Register
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <label>
                Username
                <input
                  name="username"
                  value={form.username}
                  onChange={handleInputChange}
                  minLength={3}
                  required
                />
              </label>
              <label>
                Password
                <input
                  type="password"
                  name="password"
                  value={form.password}
                  onChange={handleInputChange}
                  minLength={mode === "register" ? 6 : 1}
                  required
                />
              </label>
              {error ? <p className="error">{error}</p> : null}
              <button className="primary" type="submit" disabled={loading}>
                {loading ? "Please wait..." : mode === "login" ? "Log in" : "Create account"}
              </button>
            </form>
            <p className="hint">
              Demo only: data is stored in your browser and never leaves your device.
            </p>
          </section>
        ) : (
          <section className="card board-card">
            <div className="board-header">
              <div>
                <h2>Welcome, {user}</h2>
                <p className="subtitle">Your board and stats are private to you.</p>
              </div>
              <div className="board-actions">
                <button className="secondary" type="button" onClick={handleReset}>
                  Reset marks
                </button>
              </div>
            </div>
            <div className="view-tabs">
              <button
                type="button"
                className={view === "board" ? "active" : ""}
                onClick={() => setView("board")}
              >
                My Board
              </button>
              <button
                type="button"
                className={view === "stats" ? "active" : ""}
                onClick={() => setView("stats")}
              >
                My Stats
              </button>
            </div>
            {view === "board" ? (
              <>
                <div className="board-meta">
                  <p className="subtitle">
                    Marked {markedCount} of {board?.cells.length ?? 0} squares
                  </p>
                  <p className="subtitle">Last updated: {lastUpdated}</p>
                </div>
                {hasBingo ? <div className="bingo-banner">Bingo!</div> : null}
                <div className="board-grid">
                  {board?.cells.map((cell, index) => (
                    <button
                      key={`${cell.text}-${index}`}
                      type="button"
                      className={`cell ${cell.marked ? "marked" : ""} ${
                        index === 12 ? "free" : ""
                      }`}
                      onClick={() => handleToggle(index)}
                    >
                      <span>{cell.text}</span>
                    </button>
                  ))}
                </div>
              </>
            ) : (
              <div className="stats-grid">
                <div className="stat-card">
                  <p className="stat-label">Signed-in user</p>
                  <p className="stat-value">{user}</p>
                </div>
                <div className="stat-card">
                  <p className="stat-label">Squares marked</p>
                  <p className="stat-value">
                    {markedCount} / {board?.cells.length ?? 0}
                  </p>
                </div>
                <div className="stat-card">
                  <p className="stat-label">Last updated</p>
                  <p className="stat-value">{lastUpdated}</p>
                </div>
                <div className="stat-card">
                  <p className="stat-label">Bingo status</p>
                  <p className="stat-value">{hasBingo ? "Bingo!" : "No bingo yet"}</p>
                </div>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
