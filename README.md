# UV Tile Manager
Blender addon for managing UV tiles - select and move UV islands between tiles  
Largely made according to my friend wosted's specifications

## Features
* **Select UV Tile** - Select all UV islands within a specific tile (0-3 grid)
   * Automatically enables UV sync selection for easier workflow
   * Shows selected tile coordinates in info
* **Move to Target Tile** - Move selected UV islands to another tile position
   * Maintains relative UV positions within islands
   * Works with multiple islands at once
* **Move Off Grid** - Move selected UVs outside the 0-3 tile range
   * Default offset (4,0) places UVs safely outside standard tile range
   * Custom X/Y offsets for precise placement
   * Prevents interference with Unity UV tile discards/erasers
* **Visual Grid Reference** - Shows 4x4 grid layout with highlighted source tile

## Installation
1. Download the zip file, install through "add ons" section
2. Select the file and enable "UV: UV Tile Manager"

## Usage
1. Open UV Editor (UV Editing workspace)
2. Press N to show sidebar if hidden
3. Find "UV Tile Manager" tab
4. Select your mesh and enter Edit mode

### Basic Workflow
* Set Source Tile (X,Y) → Click "Select Tile" to grab all UVs in that tile
* Set Target Tile (X,Y) → Click "Move to Target Tile" to relocate selection
* Or use "Move Off Grid" to push selected UVs outside the working area

## Misc Things
* The grid uses 0-3 coordinates (matching standard UV tile layout)
* Moving off-grid is perfect for hiding UVs from tile-based Unity scripts
* Works with UV islands that span multiple tiles (selects if any part is in tile)
* All operations support undo (Ctrl+Z)

## Requirements
* Blender 4.0+
* Mesh with UV map
* Edit mode for UV operations

The _init_.py file is the source code and the only file in the zip folder if you need easier access to it

The `uv_tile_manager.py` file is the complete addon - no additional files needed
