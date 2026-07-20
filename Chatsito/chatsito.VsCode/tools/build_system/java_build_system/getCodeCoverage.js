const { runJavaCommand } = require('./javaHelper');

async function getCodeCoverage(projectPath) {
    return await runJavaCommand(projectPath, 'test jacoco:report', 'test jacocoTestReport');
}

module.exports = getCodeCoverage;
