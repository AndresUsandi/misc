const assert = require('assert');
const searchWorkspace = require('../searchWorkspace.js');

describe('searchWorkspace Tool', function () {
    this.timeout(20000);

    it('should search the workspace for a query', async () => {
        // Act: Search for "TargetMethod" in our fixture
        const output = await searchWorkspace('TargetMethod', '**/fixtures/TestDefinition.js');
        
        assert.ok(output, 'Output should not be null');
        assert.ok(output.includes('Search Results for: "TargetMethod"'), 'Should include header');
        assert.ok(output.includes('TestDefinition.js'), 'Should include the file name');
        assert.ok(output.includes('function TargetMethod() {'), 'Should include the matched line text');
    });

    it('should return error for empty query', async () => {
        const output = await searchWorkspace('');
        assert.strictEqual(output, 'Error: No query provided for search.');
    });

    it('should return no matches found for a nonexistent string', async () => {
        const output = await searchWorkspace('thisstringwillneverbefoundinthisworkspace', '**/fixtures/TestDefinition.js');
        assert.ok(output.includes('No matches found for query'), 'Should indicate no matches found');
    });
});
