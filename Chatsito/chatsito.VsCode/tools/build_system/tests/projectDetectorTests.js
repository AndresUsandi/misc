const assert = require('assert');
const path = require('path');
const vscode = require('vscode');
const { identifyProjectType } = require('../projectDetector');

describe('Project Detector Helper', () => {
    it('should identify dotnet project type from file extensions (fallback)', () => {
        assert.strictEqual(identifyProjectType('test.csproj'), 'dotnet');
        assert.strictEqual(identifyProjectType('test.sln'), 'dotnet');
        assert.strictEqual(identifyProjectType('Program.cs'), 'dotnet');
    });

    it('should identify npm project type from file extensions (fallback)', () => {
        assert.strictEqual(identifyProjectType('index.js'), 'npm');
        assert.strictEqual(identifyProjectType('App.tsx'), 'npm');
        assert.strictEqual(identifyProjectType('package.json'), 'npm');
    });

    it('should return null for unsupported files or null/undefined inputs', () => {
        assert.strictEqual(identifyProjectType('test.txt'), null);
        assert.strictEqual(identifyProjectType(''), 'npm'); // Defaults to workspace root, which contains package.json (npm)
    });

    it('should identify real project folders in the workspace', () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders && workspaceFolders.length > 0) {
            const root = workspaceFolders[0].uri.fsPath;
            const parentDir = path.basename(root) === 'chatsito.VsCode' ? path.dirname(root) : root;
            const vscodeDir = path.join(parentDir, 'chatsito.VsCode');
            assert.strictEqual(identifyProjectType(vscodeDir), 'npm');

            // Under chatsito.Core, it is dotnet.
            const coreDir = path.join(parentDir, 'chatsito.Core');
            assert.strictEqual(identifyProjectType(coreDir), 'dotnet');
        }
    });

    it('should identify java project type from file extensions (fallback)', () => {
        assert.strictEqual(identifyProjectType('pom.xml'), 'java');
        assert.strictEqual(identifyProjectType('build.gradle'), 'java');
        assert.strictEqual(identifyProjectType('Main.java'), 'java');
    });

    it('should identify C/C++ project type from file extensions (fallback)', () => {
        assert.strictEqual(identifyProjectType('CMakeLists.txt'), 'c');
        assert.strictEqual(identifyProjectType('Makefile'), 'c');
        assert.strictEqual(identifyProjectType('main.cpp'), 'c');
        assert.strictEqual(identifyProjectType('helper.c'), 'c');
    });

    it('should cache project type identification results', () => {
        const { clearCache } = require('../projectDetector');
        clearCache();
        
        const testPath = 'dummy.csproj';
        assert.strictEqual(identifyProjectType(testPath), 'dotnet');
        
        clearCache();
        assert.strictEqual(identifyProjectType(testPath), 'dotnet');
    });
});
