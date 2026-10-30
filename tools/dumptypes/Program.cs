using System;
using System.Linq;
using Mono.Cecil;

// usage: dumptypes <dll> <typeNameRegex> [memberRegex]
var asm = AssemblyDefinition.ReadAssembly(args[0]);
var tr = new System.Text.RegularExpressions.Regex(args[1]);
var mr = args.Length > 2 ? new System.Text.RegularExpressions.Regex(args[2]) : null;
void Walk(TypeDefinition t)
{
    if (tr.IsMatch(t.FullName))
    {
        Console.WriteLine($"{t.FullName} : {t.BaseType?.FullName}");
        foreach (var f in t.Fields.Where(f => !f.Name.StartsWith("NativeFieldInfoPtr") && (mr == null || mr.IsMatch(f.Name))))
            Console.WriteLine($"   F {f.FieldType.Name} {f.Name}");
        foreach (var p in t.Properties.Where(p => mr == null || mr.IsMatch(p.Name)))
            Console.WriteLine($"   P {p.PropertyType.Name} {p.Name}");
        foreach (var m in t.Methods.Where(m => (!m.IsSpecialName || m.Name==".ctor") && !m.Name.StartsWith("NativeMethodInfoPtr") && (mr == null || mr.IsMatch(m.Name))))
            Console.WriteLine($"   M {(m.IsStatic ? "static " : "")}{m.ReturnType.Name} {m.Name}({string.Join(", ", m.Parameters.Select(p => p.ParameterType.Name + " " + p.Name))})");
    }
    foreach (var n in t.NestedTypes) Walk(n);
}
foreach (var t in asm.MainModule.Types) Walk(t);
