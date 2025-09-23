🛠️ CMake Build System Management 🚀

Welcome to the CMake Build System Management repository! This collection of powerful CMake tools is designed to make managing multi-project workspaces fun, easy, and surprisingly satisfying. I take the chaos of dependencies and builds and transform it into a streamlined, manageable workflow, one line of code at a time.

⚡ Why this Project?

If you've ever found yourself tangled in the mess of CMake configurations and multiple projects, then this repo is your new best friend. Here, I’ve packed everything into easy-to-use CMake modules, letting you focus on the coding, while I handle the build complexity. Just like magic.

🌟 Getting Started
1. Clone the Repo

You can either clone this project directly or include it in your existing CMake project. To get started, just run:

git clone https://github.com/yourusername/your-repository.git

2. Include the CMake Modules

Add the following lines to your CMakeLists.txt file:

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/path/to/cmake")
include(BuildType)
include(AddWorkspaces)
include(AddTarget)
include(SetupPackage)
include(Uninstall)

3. Configure and Build the Project

cmake -S . -B build -DCMAKE_INSTALL_PREFIX="/path/to/install"
cmake --build build
cmake --install build

4. Uninstall (Because Cleanliness is Important)

cmake --build build --target uninstall

🧩 How To Use
in the root cmakefile
add_workspace_projects(
  ROOT "${CMAKE_SOURCE_DIR}/projects"     # Your projects directory
  MODE LEAF                              # Choose how deep to scan (FIRST | ALL | LEAF)
  ONLY   netlib utils                    # Only build these specific sub-projects
  EXCLUDE legacy                         # Exclude these sub-projects
  MAX_DEPTH 2                            # Limit the depth of recursion
)
in the sub use add_modules and AddTarget with cmakefile
2. Flexibility with Build Types

cmake -S . -B build -DPROJECT_BUILD_TYPE=Debug  # Switch to Debug
cmake --build build --config Release            # Build the Release version

3. Install and Uninstall Like a Pro

cmake --install build

cmake --build build --target uninstall

🔄 Example Workflow

Here’s how your typical workflow might look:

Clone the project: Download the repo or include it in your existing project.

Configure the build: Choose the build type and set up your project.

Build: Let CMake automatically handle the sub-projects and build everything in the right order.

Install: Push your project to the right location.

Uninstall: Remove everything cleanly when you’re done (or need to start fresh).

💡 License

This project is licensed under the MIT License
.
