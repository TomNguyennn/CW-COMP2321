# Improvement Suggestions for agent2.py

## 🔴 Critical Bugs to Fix

### 1. **Typo: 'right' should be 'rook'**
   - **Location**: Lines 13, 22, 31, 124, 144, 254
   - **Issue**: Using 'right' instead of 'rook' means rook pieces aren't being evaluated correctly
   - **Impact**: Rooks are not getting their proper piece-square table bonuses
   - **Fix**: Replace all instances of `'right'` with `'rook'`

### 2. **Endgame King Distance Logic is Reversed**
   - **Location**: Lines 275-277, 287-288 in `endgame_evaluate_position()`
   - **Issue**: 
     - Line 277: `score += distance * 10` - This rewards moving king AWAY from center (bad)
     - Line 288: `score -= distance * 10` - This penalizes opponent king being away (good, but inconsistent)
   - **Fix**: In endgame, king should move TOWARD center, so:
     - Player king: `score -= distance * 10` (closer to center = better)
     - Opponent king: `score += distance * 10` (farther from center = better for us)

### 3. **Unused Functions**
   - `is_endgame()` - Defined but never called
   - `evaluate_repetition()` - Defined but never called  
   - `filter_repeated_moves()` - Defined but never called
   - **Impact**: Repetition avoidance (your stated goal) is not working!

## 🟡 Code Quality Issues

### 4. **Bare Exception Handlers**
   - **Location**: Lines 158, 166, 279, 289, 330, 335, 356, 360, 399
   - **Issue**: `except:` catches everything, hiding bugs
   - **Fix**: Use specific exceptions like `except (AttributeError, ValueError):` or at least `except Exception as e:` and log it

### 5. **Code Duplication**
   - **Location**: `evaluate_position()` and `endgame_evaluate_position()`
   - **Issue**: ~70% of code is duplicated
   - **Fix**: Extract common evaluation logic into helper functions

### 6. **Unused Variables**
   - `white_materials`, `black_materials`, `get_starting_material()` - Never used
   - **Fix**: Remove or implement material tracking if needed

### 7. **Commented-Out Code**
   - Lines 53-59, 365-388
   - **Fix**: Remove or move to a separate file if keeping for reference

### 8. **Inconsistent Variable Naming**
   - Line 234: `our_king_pos` vs line 275: `player_king_pos`
   - **Fix**: Use consistent naming throughout

## 🟢 Algorithm Improvements

### 9. **Integrate Repetition Checking**
   - **Current**: Position history is tracked but never used in minimax
   - **Fix**: 
     - Call `filter_repeated_moves()` before searching
     - Use `evaluate_repetition()` in evaluation function
     - Penalize moves that lead to 3+ repetitions

### 10. **Use is_endgame() Function**
   - **Current**: Always uses `king_table_start_game` even in endgame
   - **Fix**: 
     ```python
     if is_endgame(board):
         king_table = king_table_mid_game  # or create endgame table
     else:
         king_table = king_table_start_game
     ```

### 11. **Add Transposition Table**
   - **Benefit**: Cache evaluated positions to avoid re-computation
   - **Implementation**: Use `board.fen()` as key, store (score, depth, flag)
   - **Impact**: Can significantly speed up search and allow deeper depths

### 12. **Add Quiescence Search**
   - **Current**: Evaluation stops at depth 0, even in tactical positions
   - **Fix**: Continue searching captures/checks until "quiet" position
   - **Impact**: Better tactical play, fewer blunders

### 13. **Improve Move Ordering**
   - **Current**: Only considers captures and center control
   - **Enhancements**:
     - Killer moves heuristic (moves that caused beta cutoffs)
     - History heuristic (track which moves are good at each depth)
     - MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
   - **Impact**: More alpha-beta cutoffs = faster search

### 14. **Checkmate/Stalemate Detection**
   - **Current**: Returns -999999/999999 for no moves, but doesn't distinguish checkmate from stalemate
   - **Fix**: Check if king is in check to distinguish checkmate vs stalemate
   - **Impact**: Better endgame play

## 🔵 Performance Optimizations

### 15. **Cache Legal Moves**
   - **Current**: `list_legal_moves_for()` called multiple times per evaluation
   - **Fix**: Cache results or pass as parameter
   - **Impact**: Reduce redundant calculations

### 16. **Optimize Position Evaluation**
   - **Current**: Loops through all pieces twice (player + opponent)
   - **Fix**: Single loop with conditional logic
   - **Impact**: ~50% reduction in evaluation time

### 17. **Early Exit Conditions**
   - Add checks for obvious wins/losses before deep search
   - Check for checkmate in 1-2 moves

## 🟣 Evaluation Function Improvements

### 18. **Clarify Move Count Weighting**
   - **Location**: Line 151, 266 - Comment says "#why?"
   - **Current**: `(player_moves - opponent_moves) * 10`
   - **Issue**: 10 might be too high, causing over-valuation of mobility
   - **Suggestion**: Reduce to 2-5, or make it depth-dependent

### 19. **Add Rook Table**
   - **Current**: Rooks use `bishop_table` (line 124, 144, 254)
   - **Fix**: Create proper `rook_table` for rook-specific positioning

### 20. **King Safety in Middlegame**
   - **Current**: Only checks if in check, no king safety evaluation
   - **Enhancement**: Evaluate pawn shield, piece attacks near king
   - **Impact**: Better defensive play

### 21. **Pawn Structure Evaluation**
   - **Current**: Only positional bonuses
   - **Enhancement**: Evaluate doubled pawns, isolated pawns, passed pawns
   - **Impact**: Better positional understanding

## 📊 Priority Recommendations

### High Priority (Fix Immediately):
1. Fix 'right' → 'rook' typo
2. Integrate repetition checking (your stated goal!)
3. Fix endgame king distance logic
4. Use `is_endgame()` to switch evaluation

### Medium Priority (Significant Impact):
5. Add transposition table
6. Add quiescence search
7. Improve move ordering
8. Remove code duplication

### Low Priority (Nice to Have):
9. Add rook table
10. Improve exception handling
11. Clean up unused code
12. Add pawn structure evaluation

## 🎯 Quick Wins (Easy to Implement)

1. **Fix the typo** - 5 minutes, immediate improvement
2. **Use is_endgame()** - 10 minutes, better endgame play
3. **Call filter_repeated_moves()** - 5 minutes, achieves your stated goal
4. **Fix king distance** - 5 minutes, better endgame
5. **Remove unused code** - 5 minutes, cleaner codebase

## 📝 Code Structure Suggestions

Consider refactoring into classes:
- `EvaluationEngine` - handles all evaluation logic
- `SearchEngine` - handles minimax and search
- `MoveOrderer` - handles move ordering heuristics
- `TranspositionTable` - caches positions

This would make the code more maintainable and testable.

# Week 10 improvement
- use white/black material counter (maybe not that useful but think about it)
- PROMOTE PAWN TO QUEEN
- use repetition to not draw


# Final improvements
- promote pawn to queen
- queen heuristic value
- use white/black material counter
- if an imporant piece is endangered, prioritize its safety


- change heuristic value for pawn in front of knight

- 10: black - time thinking this move: 0.5148866250237916
Bishop (Player (black)) move to: (2,2)
Bishop (Player (black)) captures at: (2,2)
  0 1 2 3 4
0 r . k . .
1 p . p . p
2 . . b . .
3 P . . . P
4 . K . Q R
11: white - time thinking this move: 0.7204693750245497
Queen (Player (white)) move to: (0,1)
Queen (Player (white)) captures at: (0,1)
  0 1 2 3 4
0 r . k . .
1 Q . p . p
2 . . b . .
3 P . . . P
4 . K . . R
12: black - time thinking this move: 0.7396998750045896
Right (Player (black)) move to: (0,1)
Right (Player (black)) captures at: (0,1)
  0 1 2 3 4
0 . . k . .
1 r . p . p
2 . . b . .
3 P . . . P
4 . K . . R