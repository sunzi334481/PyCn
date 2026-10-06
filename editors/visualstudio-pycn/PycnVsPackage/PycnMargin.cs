using System;
using System.ComponentModel.Composition;
using System.Windows;
using System.Windows.Controls;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Utilities;

namespace PycnVsPackage
{
    /// <summary>编辑器顶部的 PyCn 工具条，提供运行按钮。</summary>
    internal sealed class PycnMargin : IWpfTextViewMargin
    {
        public const string MarginName = "PycnMargin";

        private readonly StackPanel _panel;
        private bool _disposed;

        public PycnMargin(IWpfTextView textView, PycnRunner runner)
        {
            var button = new Button
            {
                Content = "▶ 运行 PyCn",
                Padding = new Thickness(8, 2, 8, 2),
                Margin = new Thickness(3),
                ToolTip = "运行当前 .pycn 文件（python -m pycn_lang run）"
            };
            button.Click += (s, e) => runner.Run(textView);

            _panel = new StackPanel
            {
                Orientation = Orientation.Horizontal
            };
            _panel.Children.Add(button);
        }

        public FrameworkElement VisualElement => _panel;

        public double MarginSize => _panel.ActualHeight;

        public bool Enabled => !_disposed;

        public ITextViewMargin GetTextViewMargin(string marginName) =>
            marginName == MarginName ? this : null;

        public void Dispose()
        {
            _disposed = true;
        }
    }

    [Export(typeof(IWpfTextViewMarginProvider))]
    [Name(PycnMargin.MarginName)]
    [Order(Before = PredefinedMarginNames.Outlining)]
    [MarginContainer(PredefinedMarginNames.Top)]
    [ContentType(PycnContentTypeDefinition.ContentTypeName)]
    [TextViewRole(PredefinedTextViewRoles.Document)]
    internal sealed class PycnMarginProvider : IWpfTextViewMarginProvider
    {
        [Import]
        internal Microsoft.VisualStudio.Shell.SVsServiceProvider ServiceProvider;

        public IWpfTextViewMargin CreateMargin(
            IWpfTextViewHost wpfTextViewHost,
            IWpfTextViewMargin marginContainer)
        {
            return new PycnMargin(
                wpfTextViewHost.TextView,
                new PycnRunner(ServiceProvider));
        }
    }
}
