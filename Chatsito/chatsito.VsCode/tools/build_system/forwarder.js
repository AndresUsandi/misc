const { identifyProjectType } = require('./projectDetector');

async function forwardToolRequest(toolName, targetPath, ...args) {
    const projectType = identifyProjectType(targetPath);
    if (!projectType) {
        return `Error: Unsupported or unidentified project type for path: ${targetPath || ''}`;
    }

    let subfolder;
    if (projectType === 'dotnet') {
        subfolder = 'dotnet_build_system';
    } else if (projectType === 'nodejs') {
        subfolder = 'nodejs_build_system';
    } else if (projectType === 'npm') {
        subfolder = 'npm_build_system';
    } else if (projectType === 'java') {
        subfolder = 'java_build_system';
    } else if (projectType === 'c') {
        subfolder = 'c_build_system';
    } else if (projectType === 'python') {
        subfolder = 'python_build_system';
    } else {
        return `Error: Unsupported project type '${projectType}' for tool '${toolName}'.`;
    }

    try {
        const specificTool = require(`./${subfolder}/${toolName}`);

        // Adapt signature calls dynamically depending on the project system
        if (projectType === 'dotnet') {
            if (toolName === 'buildSolution' || toolName === 'getCodeCoverage' || toolName === 'listTests' || toolName === 'runTests') {
                return await specificTool();
            } else if (toolName === 'buildProject' || toolName === 'compileFile') {
                return await specificTool(targetPath);
            } else if (toolName === 'runTest') {
                const [testName] = args;
                return await specificTool(testName);
            } else if (toolName === 'runFile') {
                const [runArgs] = args;
                return await specificTool(targetPath, runArgs);
            }
        }

        // Standard signature (projectPath/solutionPath, ...args) for npm, java, and c
        return await specificTool(targetPath, ...args);

    } catch (e) {
        return `Error executing build tool '${toolName}' for ${projectType} project: ${e.message}`;
    }
}

module.exports = {
    forwardToolRequest
};
