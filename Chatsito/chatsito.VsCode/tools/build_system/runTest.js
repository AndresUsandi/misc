const { forwardToolRequest } = require('./forwarder');

async function runTest(projectPath, testName) {
    let actualProjectPath = projectPath;
    let actualTestName = testName;

    // Handle single-argument calls where the only argument is actually the testName
    if (testName === undefined) {
        const isPath = typeof projectPath === 'string' && (
            projectPath.includes('/') || 
            projectPath.includes('\\') || 
            projectPath.endsWith('.js') || 
            projectPath.endsWith('.ts') || 
            projectPath.endsWith('.json') || 
            projectPath.endsWith('.csproj') || 
            projectPath.endsWith('.sln') ||
            projectPath.endsWith('.java') ||
            projectPath.endsWith('pom.xml') ||
            projectPath.endsWith('.gradle') ||
            projectPath.endsWith('.c') ||
            projectPath.endsWith('.cpp')
        );
        if (isPath) {
            actualProjectPath = projectPath;
            actualTestName = '';
        } else {
            actualProjectPath = undefined;
            actualTestName = projectPath;
        }
    }

    return await forwardToolRequest('runTest', actualProjectPath, actualTestName);
}

module.exports = runTest;
