# TSMC CareerHack 2025

[Hackmd Note](https://hackmd.io/@gary940610/H1jqhXXFyl)

[![Build multiarch OCI image](https://github.com/icannon2/tsmc2025/actions/workflows/docker.yml/badge.svg)](https://github.com/icannon2/tsmc2025/actions/workflows/docker.yml)
[![Conventional Commit Checker](https://github.com/icannon2/tsmc2025/actions/workflows/conventional.yml/badge.svg)](https://github.com/icannon2/tsmc2025/actions/workflows/conventional.yml)
[![Ruff](https://github.com/icannon2/tsmc2025/actions/workflows/ruff.yml/badge.svg)](https://github.com/icannon2/tsmc2025/actions/workflows/ruff.yml)

[![wakatime](https://wakatime.com/badge/user/6c7a0447-9414-43ab-a937-9081f3e9fc7d/project/ccc8a848-7a2d-4c44-8d75-950624f669a2.svg)](https://wakatime.com/badge/user/6c7a0447-9414-43ab-a937-9081f3e9fc7d/project/ccc8a848-7a2d-4c44-8d75-950624f669a2)

## Detailed Scoring Criteria

### System Architecture (30%)
- 依照架構圖發表為何如此設計
  1. 系統架構
  2. 創建使用者與資料授權設計（ex. 使用者只能看到某些公司的資料）
  3. AI Agent Processing Graph（查詢/計算數值型指標、歷年財務轉換、資料摘要等等）
  4. 避免資料幻覺

**2/15 HackDay 呈現方式：Presentation**

---

### Data Trustworthiness (30%)
- [ ] **模型支援多語系**
- [ ] **資料授權設計**（Role: 參考 workshop 投影片）
- [ ] **資料視覺化**（根據數值資料畫折線圖）
- [ ] **搜尋單一公司的財報指標與逐字稿內容**
- [ ] **跨公司的財務比較與財報指標逐字稿內容**
- [ ] **歷年財務的轉換**（參考 workshop 投影片）
- [ ] **正確的幣值轉換**（幣值轉換基準: 參考 workshop 投影片）
- [ ] **計算更多的財務指標**（財務公式: 參考 workshop 投影片）
  - 毛利率
  - 營業利益率

**2/15 HackDay 呈現方式：Questions with Chatbot**

---

### Data Summarization (15%)
- [ ] **資料範圍**：逐字稿、數值型財務指標
- [ ] **題目**：歷年季度 + 公司名稱
- [ ] **由系統生成摘要報告**，內容可自由發揮，建議方向（不限）：
   - 財務數據趨勢
   - 產品策略
   - 市場競合
   - 未來展望（可讀性 / 資料視覺化）

**2/15 HackDay 呈現方式：Presentation**

---

### User Experience & UI Friendliness (15%)
1. **前端互動的介面**
2. **資料視覺化、資料標註**

**2/15 HackDay 呈現方式：Live demo & presentation**

---

### Bonus (10%)
- 其他功能、創意

**2/15 HackDay 呈現方式：Live demo & presentation**

## Development Environment Setup

Welcome to the project! This README will guide you through setting up your development environment using a dev container. A dev container simplifies the setup process and ensures that you have a consistent development environment.

### Prerequisites

Before you get started, make sure you have the following installed on your machine:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker](https://www.docker.com/get-started)
- [Remote - Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Getting Started

Follow these steps to set up your development environment using a dev container:

1. **Clone the Repository**

   Begin by cloning the repository to your local machine. Open your terminal and run:

   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. **Open the Project in Visual Studio Code**

   Launch Visual Studio Code and open the project directory that you just cloned.

   ```bash
   code .
   ```

3. **Reopen in Container**

   Once you have the project open in VS Code, you should see a prompt to reopen the folder in a container. Click on the prompt labeled **Reopen in Container**. This action will trigger Docker to build the necessary environment based on the configuration files (`Dockerfile` and `devcontainer.json`).

   If you don’t see the prompt, you can manually trigger it by opening the Command Palette (Ctrl+Shift+P or Cmd+Shift+P on Mac) and selecting **Remote-Containers: Reopen in Container**.

4. **Wait for the Container to Build**

   Docker will automatically build the container and install the required dependencies defined in the Dockerfile. This process may take a few minutes, especially on the first build.

5. **Verify Your Setup**

   Once the container is running, open a new terminal in VS Code (Terminal > New Terminal). You can verify that everything is set up correctly by running:

   ```bash
   python -V
   uv run app.py
   ```

   Replace these commands with any other commands you might need to verify based on the tech stack being used in this project.

### Development Workflow

After setting up the dev container, you can proceed with development as follows:

- **Editing Files**: Modify code files in the project as needed. Changes made will reflect in the container.
- **Running Commands**: Use the integrated terminal to run commands and scripts specific to your project without leaving the VS Code interface.
- **Debugging**: Set breakpoints and debug your application directly within the VS Code environment.

### Additional Resources

- **For Docker**: Learn more about Docker and containerization [here](https://docs.docker.com/get-started/).
- **For VS Code Remote Development**: Explore the official documentation for Remote - Containers [here](https://code.visualstudio.com/docs/remote/containers).

---

Happy coding! 🎉