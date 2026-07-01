const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const lookupPackage = require('../lookupPackage.js');

describe('lookupPackage Tool', function () {
    this.timeout(10000);

    let testDir;
    let pkgPath;
    let csprojPath;
    let originalPackageJson = null;
    let hadPackageJson = false;

    before(() => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        testDir = workspaceFolders[0].uri.fsPath;
        
        pkgPath = path.join(testDir, 'package.json');
        csprojPath = path.join(testDir, 'test-proj.csproj');

        if (fs.existsSync(pkgPath)) {
            hadPackageJson = true;
            originalPackageJson = fs.readFileSync(pkgPath);
        }

        fs.writeFileSync(pkgPath, JSON.stringify({
            dependencies: { "react": "^18.0.0" },
            devDependencies: { "mocha": "10.2.0" }
        }));

        fs.writeFileSync(csprojPath, `
            <Project>
                <ItemGroup>
                    <PackageReference Include="Newtonsoft.Json" Version="13.0.1" />
                </ItemGroup>
            </Project>
        `);
    });

    after(() => {
        if (hadPackageJson) {
            fs.writeFileSync(pkgPath, originalPackageJson);
        } else {
            if (fs.existsSync(pkgPath)) fs.unlinkSync(pkgPath);
        }
        if (fs.existsSync(csprojPath)) fs.unlinkSync(csprojPath);
    });

    it('should successfully lookup package in package.json', async () => {
        const output1 = await lookupPackage('react');
        assert.ok(output1.includes('Found package "react"'), `Output: ${output1}`);
        assert.ok(output1.includes('^18.0.0'));

        const output2 = await lookupPackage('mocha');
        assert.ok(output2.includes('10.2.0'));
    });

    it('should successfully lookup package in .csproj', async () => {
        // Wait a bit for findFiles to index the newly created csproj
        await new Promise(r => setTimeout(r, 1000));
        
        const output = await lookupPackage('Newtonsoft.Json');
        assert.ok(output.includes('Found package "Newtonsoft.Json"'), `Output: ${output}`);
        assert.ok(output.includes('13.0.1'));
    });

    it('should return message if package not found', async () => {
        const output = await lookupPackage('unknown-pkg');
        assert.ok(output.includes('not found in package.json or .csproj'));
    });

    it('should return error for missing parameters', async () => {
        const output = await lookupPackage('');
        assert.strictEqual(output, 'Error: Missing packageName parameter.');
    });
});
