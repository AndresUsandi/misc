using System;

namespace TestNamespace
{
    public class TargetClass
    {
        public void TargetMethod()
        {
            Console.WriteLine("Hello from target!");
        }
    }

    public class SourceClass
    {
        public void CallerMethod()
        {
            var target = new TargetClass();
            target.TargetMethod();
        }
    }
}
