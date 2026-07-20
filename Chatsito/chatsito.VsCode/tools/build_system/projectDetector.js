const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

const projectTypeCache = new Map();

function clearCache() {
    projectTypeCache.clear();
}

function resolvePath(targetPath) {
    if (!targetPath) {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders && workspaceFolders.length > 0) {
            return workspaceFolders[0].uri.fsPath;
        }
        return null;
    }
    if (path.isAbsolute(targetPath)) {
        return targetPath;
    }
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders && workspaceFolders.length > 0) {
        return path.resolve(workspaceFolders[0].uri.fsPath, targetPath);
    }
    return path.resolve(targetPath);
}

function checkContentForDotnet(content) {
    if (content.includes('<Project') || content.includes('<PropertyGroup') || content.includes('<ItemGroup')) {
        return true;
    }
    if (content.includes('Microsoft Visual Studio Solution File')) {
        return true;
    }
    if (content.includes('using System;') || content.includes('namespace ') || content.includes('public class ') || content.includes('static void Main')) {
        return true;
    }
    return false;
}

function checkContentForNpm(content) {
    if (content.includes('"dependencies"') || content.includes('"devDependencies"') || content.includes('"scripts"')) {
        return true;
    }
    if (content.includes('require(') || content.includes('module.exports') || content.includes('export default') || content.includes('import ')) {
        return true;
    }
    return false;
}

function checkContentForJava(content) {
    if (content.includes('<project') && content.includes('<modelVersion>')) {
        return true;
    }
    if (content.includes('plugins {') && (content.includes('id \'java\'') || content.includes('id("java")'))) {
        return true;
    }
    if (content.includes('package ') && (content.includes('import java.') || content.includes('public class ') || content.includes('class '))) {
        if (content.includes('public static void main(String[] args)') || content.includes('public static void main(String args[])')) {
            return true;
        }
    }
    return false;
}

function checkContentForC(content) {
    if (content.includes('#include ') || content.includes('#define ')) {
        return true;
    }
    if (content.includes('int main(') || content.includes('int main (')) {
        return true;
    }
    if (content.includes('using namespace std;')) {
        return true;
    }
    return false;
}

function checkContentForPython(content) {
    if (content.includes('import ') || content.includes('from ') || content.includes('def ') || content.includes('class ')) {
        if (content.includes('def ') || content.includes('import os') || content.includes('import sys') || content.includes('__main__') || content.includes('print(')) {
            return true;
        }
    }
    return false;
}

function identifyProjectType(targetPath) {
    const absPath = resolvePath(targetPath);
    if (absPath && projectTypeCache.has(absPath)) {
        return projectTypeCache.get(absPath);
    }

    const result = identifyProjectTypeImpl(absPath, targetPath);
    
    if (absPath) {
        projectTypeCache.set(absPath, result);
    }
    return result;
}

function identifyProjectTypeImpl(absPath, targetPath) {
    if (!absPath || !fs.existsSync(absPath)) {
        // Fallback: guess from extension of the unresolved/resolved path if we can
        const ext = path.extname(targetPath || '').toLowerCase();
        if (['.csproj', '.fsproj', '.vbproj', '.sln', '.cs'].includes(ext)) {
            return 'dotnet';
        }
        if (['.js', '.ts', '.jsx', '.tsx', '.json'].includes(ext)) {
            return 'npm';
        }
        if (['.java', '.jar', '.class'].includes(ext) || (targetPath && (targetPath.endsWith('pom.xml') || targetPath.endsWith('build.gradle') || targetPath.endsWith('build.gradle.kts')))) {
            return 'java';
        }
        if (['.c', '.cpp', '.h', '.hpp', '.cc', '.cxx', '.hh', '.hxx'].includes(ext) || (targetPath && (targetPath.endsWith('CMakeLists.txt') || targetPath.toLowerCase().endsWith('makefile')))) {
            return 'c';
        }
        if (['.py', '.pyw', '.ipynb'].includes(ext) || (targetPath && (targetPath.endsWith('requirements.txt') || targetPath.endsWith('pyproject.toml') || targetPath.endsWith('pipfile') || targetPath.endsWith('setup.py')))) {
            return 'python';
        }
        return null;
    }

    const stat = fs.statSync(absPath);
    if (stat.isFile()) {
        const filename = path.basename(absPath).toLowerCase();
        const ext = path.extname(absPath).toLowerCase();

        if (['.csproj', '.fsproj', '.vbproj', '.sln', '.cs'].includes(ext)) {
            return 'dotnet';
        }
        if (filename === 'package.json' || filename === 'package-lock.json' || ['.js', '.ts', '.jsx', '.tsx'].includes(ext)) {
            return 'npm';
        }
        if (['.java', '.jar', '.class'].includes(ext) || filename === 'pom.xml' || filename === 'build.gradle' || filename === 'build.gradle.kts') {
            return 'java';
        }
        if (['.c', '.cpp', '.h', '.hpp', '.cc', '.cxx', '.hh', '.hxx'].includes(ext) || filename === 'cmakelists.txt' || filename === 'makefile') {
            return 'c';
        }
        if (['.py', '.pyw', '.ipynb'].includes(ext) || filename === 'requirements.txt' || filename === 'pyproject.toml' || filename === 'pipfile' || filename === 'setup.py') {
            return 'python';
        }

        // Check content
        try {
            const content = fs.readFileSync(absPath, 'utf8');
            if (checkContentForDotnet(content)) return 'dotnet';
            if (checkContentForNpm(content)) return 'npm';
            if (checkContentForJava(content)) return 'java';
            if (checkContentForC(content)) return 'c';
            if (checkContentForPython(content)) return 'python';
        } catch (e) {
            // Ignore read errors
        }
    } else if (stat.isDirectory()) {
        try {
            const files = fs.readdirSync(absPath);
            const filesLower = files.map(f => f.toLowerCase());
            
            // Check for direct configuration files first
            if (filesLower.includes('package.json')) return 'npm';
            if (filesLower.includes('pom.xml') || filesLower.includes('build.gradle') || filesLower.includes('build.gradle.kts')) return 'java';
            if (filesLower.includes('cmakelists.txt') || filesLower.includes('makefile')) return 'c';
            if (filesLower.includes('requirements.txt') || filesLower.includes('pyproject.toml') || filesLower.includes('pipfile') || filesLower.includes('setup.py')) return 'python';
            if (files.some(f => f.toLowerCase().endsWith('.sln') || f.toLowerCase().endsWith('.csproj'))) return 'dotnet';

            // Check extensions
            if (files.some(f => ['.csproj', '.fsproj', '.vbproj', '.sln', '.cs'].includes(path.extname(f).toLowerCase()))) {
                return 'dotnet';
            }
            if (files.some(f => ['.java', '.class'].includes(path.extname(f).toLowerCase()))) {
                return 'java';
            }
            if (files.some(f => ['.c', '.cpp', '.h', '.hpp', '.cc', '.cxx', '.hh', '.hxx'].includes(path.extname(f).toLowerCase()))) {
                return 'c';
            }
            if (files.some(f => ['.py', '.pyw'].includes(path.extname(f).toLowerCase()))) {
                return 'python';
            }
            if (files.some(f => ['.js', '.ts', '.jsx', '.tsx'].includes(path.extname(f).toLowerCase()))) {
                return 'npm';
            }

            // Check content of files in the folder (up to a few files)
            for (const file of files) {
                const fileAbsPath = path.join(absPath, file);
                try {
                    const fileStat = fs.statSync(fileAbsPath);
                    if (fileStat.isFile()) {
                        const content = fs.readFileSync(fileAbsPath, 'utf8');
                        if (checkContentForDotnet(content)) return 'dotnet';
                        if (checkContentForNpm(content)) return 'npm';
                        if (checkContentForJava(content)) return 'java';
                        if (checkContentForC(content)) return 'c';
                        if (checkContentForPython(content)) return 'python';
                    }
                } catch (e) {}
            }
        } catch (e) {
            // Ignore directory read errors
        }
    }

    return null;
}

module.exports = {
    identifyProjectType,
    resolvePath,
    clearCache
};
