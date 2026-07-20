const assert = require('assert');
const getCodeCoverage = require('../getCodeCoverage.js');

describe('getCodeCoverage Tool', function () {
    this.timeout(20000);

    it('should invoke dotnet test --collect and return execution result', async () => {
        const output = await getCodeCoverage();
        
        assert.ok(output.includes('Code Coverage Collection'), `Output: ${output}`);
        assert.ok(output.includes('coverage.cobertura.xml'), 'Should contain the coverage note');
        
        assert.ok(output.includes('MSB1003') || output.includes('MSB1009') || output.toLowerCase().includes('dotnet') || output.toLowerCase().includes('error'), 'Should capture dotnet output');
    });
});
