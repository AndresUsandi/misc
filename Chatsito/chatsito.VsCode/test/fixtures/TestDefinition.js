function TargetMethod() {
    console.log("Hello from target!");
}

function CallerMethod() {
    TargetMethod();
}

module.exports = { TargetMethod, CallerMethod };
