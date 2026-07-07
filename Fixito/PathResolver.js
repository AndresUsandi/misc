import path from 'path';

class PathResolver {
    resolveAndValidateWorkspacePath(filePath) {
        if (!filePath) {
            throw new Error("No file path provided.");
        }
        
        const resolved = path.isAbsolute(filePath) ? filePath : path.resolve(process.cwd(), filePath);
        const root = path.resolve(process.cwd());
        if (!resolved.startsWith(root)) {
            throw new Error(`Path '${filePath}' is outside the workspace root '${root}'`);
        }
        
        return resolved;
    }
}

export default new PathResolver();
