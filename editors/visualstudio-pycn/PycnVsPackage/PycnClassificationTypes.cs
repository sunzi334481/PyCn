using System.ComponentModel.Composition;
using Microsoft.VisualStudio.Text.Classification;
using Microsoft.VisualStudio.Utilities;

namespace PycnVsPackage
{
    /// <summary>PyCn 语法元素的分类类型定义。</summary>
    internal static class PycnClassificationTypes
    {
        public const string Keyword = "PycnKeyword";
        public const string Builtin = "PycnBuiltin";
        public const string ExceptionName = "PycnException";
        public const string Comment = "PycnComment";
        public const string String = "PycnString";
        public const string Number = "PycnNumber";

        [Export]
        [Name(Keyword)]
        internal static ClassificationTypeDefinition KeywordType;

        [Export]
        [Name(Builtin)]
        internal static ClassificationTypeDefinition BuiltinType;

        [Export]
        [Name(ExceptionName)]
        internal static ClassificationTypeDefinition ExceptionType;

        [Export]
        [Name(Comment)]
        internal static ClassificationTypeDefinition CommentType;

        [Export]
        [Name(String)]
        internal static ClassificationTypeDefinition StringType;

        [Export]
        [Name(Number)]
        internal static ClassificationTypeDefinition NumberType;
    }
}
