const { runCCommand, getCBuildSystem, resolvePath } = require('./cHelper');
const fs = require('fs');

async function buildSolution(solutionPath) {
    const absPath = resolvePath(solutionPath);
    const system = getCBuildSystem(absPath);
    
    let gccCmd = 'gcc *.c -o main';
    if (system.type === 'gcc') {
        try {
            const files = fs.readdirSync(system.dirPath);
            const hasCpp = files.some(f => ['.cpp', '.cc', '.cxx'].includes(fs.extname(f).toLowerCase()));
            if (hasCpp) {
                gccCmd = 'g++ *.cpp -o main';
            }
        } catch (e) {}
    }

    return await runCCommand(solutionPath, 'cmake . && cmake --build .', 'make all', gccCmd);
}

module.exports = buildSolution;
