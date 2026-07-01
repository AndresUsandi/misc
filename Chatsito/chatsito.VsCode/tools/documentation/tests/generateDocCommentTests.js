const assert = require('assert');
const generateDocComment = require('../generateDocComment.js');

describe('generateDocComment Tool', function () {
    this.timeout(10000);

    it('should generate JSDoc for JavaScript signature', async () => {
        const output = await generateDocComment('function add(a, b)');
        assert.ok(output.includes('/**'), `Output: ${output}`);
        assert.ok(output.includes('* @param {any} a'));
        assert.ok(output.includes('* @param {any} b'));
        assert.ok(output.includes('* @returns {any}'));
    });

    it('should generate XML Docs for C# signature', async () => {
        const output = await generateDocComment('public int Calculate(int x, string y)');
        assert.ok(output.includes('/// <summary>'), `Output: ${output}`);
        assert.ok(output.includes('/// <param name="x">'));
        assert.ok(output.includes('/// <param name="y">'));
        assert.ok(output.includes('/// <returns>'));
    });

    it('should handle parameterless functions', async () => {
        const output = await generateDocComment('void DoSomething()');
        // Not C# since no public/private keyword, so JS
        assert.ok(output.includes('/**'), `Output: ${output}`);
        assert.ok(!output.includes('@param'));
    });

    it('should return error for missing parameters', async () => {
        const output = await generateDocComment('');
        assert.strictEqual(output, 'Error: Missing signature parameter.');
    });
});
