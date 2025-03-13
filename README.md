# Chess Engine

A Python-based chess engine that implements board representation, move generation, position evaluation, and search algorithms.

## Features

- Chess board representation
- Legal move generation
- Position evaluation
- Minimax search with alpha-beta pruning
- Simple command-line interface for playing against the engine

## Installation

1. Clone this repository
2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

## Usage

Run the main script to start a game against the engine:
```
python -m chess_engine.main
```

## Project Structure

- `chess_engine/board/`: Board representation and move generation
- `chess_engine/engine/`: Search algorithms and position evaluation
- `chess_engine/utils/`: Utility functions
- `chess_engine/main.py`: Main entry point for the application 