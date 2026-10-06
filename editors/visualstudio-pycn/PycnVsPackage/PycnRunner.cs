using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Editor;

namespace PycnVsPackage
{
    /// <summary>启动 python -m pycn_lang run 并把输出写入 VS 输出窗口的 PyCn 面板。</summary>
    internal sealed class PycnRunner
    {
        private static readonly Guid PaneGuid =
            new Guid("B85D44D1-A390-43BA-BB37-D66672569F5A");

        private readonly SVsServiceProvider _serviceProvider;

        public PycnRunner(SVsServiceProvider serviceProvider)
        {
            _serviceProvider = serviceProvider;
        }

        public void Run(IWpfTextView textView)
        {
            var path = GetFilePath(textView.TextBuffer);
            if (path == null) return;

            var pane = GetPane();
            pane?.Activate();
            pane?.OutputStringThreadSafe(
                $"==> python -m pycn_lang run \"{path}\"{Environment.NewLine}");

            var startInfo = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = $"-m pycn_lang run \"{path}\"",
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8,
                WorkingDirectory = Path.GetDirectoryName(path) ?? string.Empty
            };

            var process = new Process { StartInfo = startInfo, EnableRaisingEvents = true };

            process.OutputDataReceived += (s, args) =>
            {
                if (args.Data != null)
                {
                    pane?.OutputStringThreadSafe(args.Data + Environment.NewLine);
                }
            };
            process.ErrorDataReceived += (s, args) =>
            {
                if (args.Data != null)
                {
                    pane?.OutputStringThreadSafe(args.Data + Environment.NewLine);
                }
            };

            try
            {
                process.Start();
                process.BeginOutputReadLine();
                process.BeginErrorReadLine();
            }
            catch (Exception ex)
            {
                pane?.OutputStringThreadSafe(
                    "无法启动 python，请确认 Python 已安装并在 PATH 中：" +
                    ex.Message + Environment.NewLine);
            }
        }

        private static string GetFilePath(ITextBuffer buffer)
        {
            if (buffer.Properties.TryGetProperty<ITextDocument>(
                typeof(ITextDocument),
                out var document))
            {
                return document.FilePath;
            }
            return null;
        }

        private IVsOutputWindowPane GetPane()
        {
            var outputWindow = (IVsOutputWindow)_serviceProvider.GetService(
                typeof(SVsOutputWindow));
            if (outputWindow == null) return null;

            var paneGuid = PaneGuid;
            outputWindow.CreatePane(ref paneGuid, "PyCn", 1, 1);
            outputWindow.GetPane(ref paneGuid, out var pane);
            return pane;
        }
    }
}
