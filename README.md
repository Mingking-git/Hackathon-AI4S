# 光塑 Blender AI MCP Integration 🚀

本项目实现了一个 **Blender 扩展 + Python 客户端 + MCP 服务**，用于通过 JSON 指令或 AI 模型生成来远程控制 Blender。

## 📂 项目结构

- **`blender-addon.py`**  
  Blender 插件（Addon）。在 Blender 内运行一个 TCP 服务器，接收外部 JSON 命令并在场景中执行：
  - 创建基础几何体（立方体、球体、雪人）。
  - 导入 3D 模型（支持 OBJ/GLTF/FBX）。
  - 执行任意 Python 脚本。
  - 运行物理仿真，并支持烘焙和渲染。

- **`blender_client.py`**  
  Python 客户端脚本。通过 TCP 向 Blender 服务器发送 JSON 命令。  
  支持：
  - 手动命令输入（cube/sphere/snowman）。
  - AI 生成模型（示例中模拟了一个 Text-to-3D API）。
  - 自定义 Python 脚本下发。

- **`blender-mcp.py`**  
  MCP（Model Context Protocol）服务，基于 `fastmcp`。  
  定义了可供 AI 使用的工具函数，例如：
  - `draw_cube_in_blender`
  - `draw_sphere_in_blender`
  - `draw_shapes_in_blender`
  - `draw_shapes_in_blender_by_python`
  - `simulation_in_blender_by_python`

  这些工具会调用 `blender_client`，最终驱动 Blender。

---

## ⚙️ 安装与使用

### 1. 安装 Blender 插件
1. 打开 Blender。
2. 进入 `Edit > Preferences > Add-ons`。
3. 点击 **Install...**，选择 `blender-addon.py`。
4. 启用插件（勾选复选框）。
5. 在 **3D 视图 > N 面板 > AI MCP 标签** 中找到服务器控制面板。  
   可以启动/停止 JSON 服务器。

### 2. 启动服务器
在插件面板中点击 **Start Server**。  
默认监听 `localhost:9876`。

### 3. 使用客户端发送命令
运行：
```bash
python blender_client.py
```
示例交互：
```
--- MCP Server for Blender (AI Edition) ---
Commands:
  'cube', 'sphere', 'snowman' - for procedural objects
  'ai <your prompt>'          - to generate a model with AI
  'exit'                      - to quit

Enter command > cube
```

### 4. 使用 MCP 服务
运行：
```bash
python blender-mcp.py
```
MCP 会暴露工具给 AI，允许 AI 通过 MCP 协议调用 Blender 指令。  

---

## 🧩 示例指令

- **创建立方体**
```json
{"command": "create_cube", "params": {"size": 2, "location": [0, 0, 1]}}
```

- **运行物理仿真**
```json
{"command": "run_physics_simulation", "params": {"script": "bpy.ops.mesh.primitive_cube_add(size=2, location=[0,0,1])"}}
```

---

## 🔮 后续扩展
- 将 `blender_client.py` 中的 `call_ai_text_to_3d_api` 替换为真实的 Text-to-3D API。  
- 扩展 `blender-addon.py`，支持更多物理模拟与渲染控制。  
- 集成到更大规模的 AI MCP 应用中，让 AI 能自然地生成并操控 Blender 场景。  
