const { runCCommand, getCBuildSystem, resolvePath } = require('./cHelper');
const fs = require('fs');

async function getCodeCoverage(projectPath) {
    const absPath = resolvePath(projectPath);
    const system = getCBuildSystem(absPath);
    
    let gccCmd = 'gcc -fprofile-arcs -ftest-coverage *.c -o test_runner && ./test_runner && gcov *.c';
    if (system.type === 'gcc') {
        try {
            const files = fs.readdirSync(system.dirPath);
            const hasCpp = files.some(f => ['.cpp', '.cc', '.cxx'].includes(fs.extname(f).toLowerCase()));
            if (hasCpp) {
                gccCmd = 'g++ -fprofile-arcs -ftest-coverage *.cpp -o test_runner && ./test_runner && gcov *.cpp';
            }
        } catch (e) {}
    }

    return await runCCommand(projectPath, 'cmake -DCOVERAGE=ON . && cmake --build . && ctest', 'make coverage', gccCmd);
}

module.exports = getCodeCoverage;
