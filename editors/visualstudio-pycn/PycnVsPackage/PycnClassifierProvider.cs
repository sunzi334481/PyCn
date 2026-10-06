using System.ComponentModel.Composition;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Classification;
using Microsoft.VisualStudio.Utilities;

namespace PycnVsPackage
{
    /// <summary>为 pycn 内容类型提供分类器。</summary>
    [Export(typeof(IClassifierProvider))]
    [ContentType(PycnContentTypeDefinition.ContentTypeName)]
    internal sealed class PycnClassifierProvider : IClassifierProvider
    {
        [Import]
        internal IClassificationTypeRegistryService ClassificationRegistry;

        public IClassifier GetClassifier(ITextBuffer textBuffer)
        {
            return textBuffer.Properties.GetOrCreateSingletonProperty(
                () => new PycnClassifier(ClassificationRegistry));
        }
    }
}
