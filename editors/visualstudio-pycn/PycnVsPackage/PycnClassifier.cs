using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Classification;

namespace PycnVsPackage
{
    /// <summary>PyCn 语法高亮分类器。关键字集合与 pycn_lang/mappings.py 保持一致。</summary>
    internal sealed class PycnClassifier : IClassifier
    {
        private readonly IClassificationType _keyword;
        private readonly IClassificationType _builtin;
        private readonly IClassificationType _exception;
        private readonly IClassificationType _comment;
        private readonly IClassificationType _string;
        private readonly IClassificationType _number;

        private static readonly Regex _regex = BuildRegex();

        internal PycnClassifier(IClassificationTypeRegistryService registry)
        {
            _keyword = registry.GetClassificationType(PycnClassificationTypes.Keyword);
            _builtin = registry.GetClassificationType(PycnClassificationTypes.Builtin);
            _exception = registry.GetClassificationType(PycnClassificationTypes.ExceptionName);
            _comment = registry.GetClassificationType(PycnClassificationTypes.Comment);
            _string = registry.GetClassificationType(PycnClassificationTypes.String);
            _number = registry.GetClassificationType(PycnClassificationTypes.Number);
        }

        public IList<ClassificationSpan> GetClassificationSpans(SnapshotSpan span)
        {
            var result = new List<ClassificationSpan>();

            var lineStart = span.Start.GetContainingLine().Start;
            var lineEnd = span.End.GetContainingLine().End;
            var full = new SnapshotSpan(lineStart, lineEnd);
            var text = full.GetText();

            foreach (Match match in _regex.Matches(text))
            {
                IClassificationType type = null;
                if (match.Groups["comment"].Success) type = _comment;
                else if (match.Groups["string"].Success) type = _string;
                else if (match.Groups["number"].Success) type = _number;
                else if (match.Groups["keyword"].Success) type = _keyword;
                else if (match.Groups["builtin"].Success) type = _builtin;
                else if (match.Groups["exception"].Success) type = _exception;

                if (type != null)
                {
                    var classified = new SnapshotSpan(
                        full.Snapshot,
                        new Span(full.Start.Position + match.Index, match.Length));
                    result.Add(new ClassificationSpan(classified, type));
                }
            }
            return result;
        }

#pragma warning disable 67
        public event EventHandler<ClassificationChangedEventArgs> ClassificationChanged;
#pragma warning restore 67

        private static Regex BuildRegex()
        {
            string keywords = string.Join("|", Keywords);
            string builtins = string.Join("|", Builtins);
            string exceptions = string.Join("|", Exceptions);

            string strings =
                @"(?<string>(?:格|原|字|f|r|b|fr|rf|br|rb)?(?:""""""[\s\S]*?""""""|'''[\s\S]*?'''|""(?:\\.|[^""\\\r\n])*""|'(?:\\.|[^'\\\r\n])*'))";

            string pattern =
                @"(?<comment>#[^\r\n]*)" +
                "|" + strings +
                @"|(?<number>\b(?:0[xX][0-9a-fA-F_]+|0[bB][01_]+|0[oO][0-7_]+|\d[\d_]*(?:\.\d[\d_]*)?(?:[eE][+-]?\d[\d_]*)?[jJ]?))" +
                "|(?<keyword>(?<![\\u4e00-\\u9fff])(" + keywords + @")(?![\u4e00-\u9fff]))" +
                "|(?<builtin>(?<![\\u4e00-\\u9fff])(" + builtins + @")(?![\u4e00-\u9fff]))" +
                "|(?<exception>(?<![\\u4e00-\\u9fff])(" + exceptions + @")(?![\u4e00-\u9fff]))";

            return new Regex(pattern, RegexOptions.Compiled | RegexOptions.CultureInvariant);
        }

        private static readonly string[] Keywords =
        {
            "如果", "否则若", "否则", "对于", "在", "当", "跳出", "继续",
            "返回", "生成", "来自", "匹配", "情形", "是", "尝试", "捕获",
            "最终", "抛出", "导入", "从", "作为", "伴随", "断言", "删除",
            "全局", "非局部", "异步", "等待", "跳过", "匿名", "且", "或",
            "非", "不在", "不是", "真", "假", "空"
        };

        private static readonly string[] Builtins =
        {
            "打印", "输入", "长度", "范围", "整数", "浮点", "复数", "字符串",
            "布尔", "列表", "字典", "元组", "集合", "冻结集合", "字节", "字节数组",
            "内存视图", "类型", "是实例", "是子类", "有属性", "取属性", "设属性", "删属性",
            "超类", "属性", "静态方法", "类方法", "绝对值", "最小值", "最大值", "求和",
            "排序", "反序", "枚举", "打包", "映射", "过滤", "任一", "全部",
            "四舍五入", "商余", "幂", "字符", "序号", "十六进制", "二进制", "八进制",
            "可迭代", "下一个", "切片", "打开", "求值", "执行", "编译", "帮助",
            "目录", "标识", "哈希", "表示", "变量", "全局变量", "局部变量", "断点",
            "退出"
        };

        private static readonly string[] Exceptions =
        {
            "根异常", "异常", "系统退出", "键盘中断", "生成器退出", "停止迭代", "停止异步迭代", "算术错误",
            "零除错误", "溢出错误", "浮点错误", "断言错误", "属性错误", "缓冲错误", "末尾错误", "导入错误",
            "模块未找到错误", "查找错误", "索引错误", "键错误", "名称错误", "未绑定局部错误", "环境错误", "阻塞错误",
            "子进程错误", "连接错误", "连接断开错误", "连接拒绝错误", "连接重置错误", "文件存在错误", "文件未找到错误", "中断错误",
            "是目录错误", "不是目录错误", "权限错误", "进程查找错误", "超时错误", "引用错误", "运行时错误", "未实现错误",
            "递归错误", "语法错误", "缩进错误", "制表符错误", "系统错误", "类型错误", "值错误", "万国码错误",
            "编码错误", "解码错误", "翻译错误", "内存错误", "警告基类", "用户警告", "弃用警告", "未来警告",
            "挂起弃用警告", "语法警告", "运行时警告", "导入警告", "万国码警告", "字节警告", "资源警告"
        };
    }
}
