using System.ComponentModel.Composition;
using Microsoft.VisualStudio.Utilities;

namespace PycnVsPackage
{
    /// <summary>注册 pycn 内容类型并把 .pycn 扩展名关联到该类型。</summary>
    internal static class PycnContentTypeDefinition
    {
        public const string ContentTypeName = "pycn";

        [Export]
        [Name(ContentTypeName)]
        [BaseDefinition("text")]
        internal static ContentTypeDefinition PycnContentType;

        [Export]
        [FileExtension(".pycn")]
        [ContentType(ContentTypeName)]
        internal static FileExtensionToContentTypeDefinition PycnFileExtension;
    }
}
