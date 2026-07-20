const { runCCommand, getCBuildSystem, resolvePath } = require('./cHelper');
const fs = require('fs');

async function buildProject(projectPath) {
    if (!projectPath) return "Error: Missing projectPath parameter.";
    
    const absPath = resolvePath(projectPath);
    const system = getCBuildSystem(absPath);
    
    let gccCmd = 'gcc -c *.c';
    if (system.type === 'gcc') {
        try {
            const files = fs.readdirSync(system.dirPath);
            const hasCpp = files.some(f => ['.cpp', '.cc', '.cxx'].includes(fs.extname(f).toLowerCase()));
            if (hasCpp) {
                gccCmd = 'g++ -c *.cpp';
            }
        } catch (e) {}
    }

    return await runCCommand(projectPath, 'cmake --build .', 'make', gccCmd);
}

module.exports = buildProject;
