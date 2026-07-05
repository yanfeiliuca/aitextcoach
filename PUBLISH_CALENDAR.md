# AITextCoach 博客发布日历

> 6篇待发布文章，从 7月5日 到 7月10日，每天一篇

## 发布规则
- 每天从 `blog-to-publish/` 移一篇到 `blog/`
- 更新文章日期为当天
- 提交并推送到 GitHub
- 触发网站重新部署（如已配置自动部署）

---

| 日期 | 篇号 | 文件名 | 发布状态 | 标题 |
|------|------|--------|----------|------|
| 7月3日 | 1 | ai-humanizer-passes-turnitin.html | ✅ 已发 | AI Humanizer That Passes Turnitin: How It Works |
| 7月4日 | 2 | ai-writing-enhancer-free.html | ✅ 已发 | AI Writing Enhancer Free: What You Actually Get |
| **7月5日** | 3 | **best-ai-text-rewriter-for-students.html** | ⏳ **今天** | Best AI Text Rewriter for Students: What to Look For |
| 7月6日 | 4 | free-ai-humanizer-online.html | ⏳ 待发布 | Free AI Humanizer Online: No Signup Required |
| 7月7日 | 5 | how-to-make-ai-text-sound-human.html | ⏳ 待发布 | How to Make AI Text Sound Human: The 5 Tells That Give It Away |
| 7月8日 | 6 | how-to-make-chatgpt-output-sound-human.html | ⏳ 待发布 | How to Make ChatGPT Output Sound Human: A Step-by-Step Guide |
| 7月9日 | 7 | how-to-remove-ai-detection-from-text.html | ⏳ 待发布 | How to Remove AI Detection from Text: A Practical Guide |
| 7月10日 | 8 | why-does-ai-writing-sound-robotic.html | ⏳ 待发布 | Why Does My AI Writing Sound Robotic? (And How to Fix It) |

---

## 每日发布命令（复制执行）

### 7月5日 — 第3篇
```bash
cd ~/Desktop/aitextcoach
mv blog-to-publish/best-ai-text-rewriter-for-students.html blog/
sed -i '' 's/June 30, 2026/July 5, 2026/g' blog/best-ai-text-rewriter-for-students.html
git add .
git commit -m "Publish blog post 3/8: best-ai-text-rewriter-for-students (July 5)"
git push origin main
```

### 7月6日 — 第4篇
```bash
cd ~/Desktop/aitextcoach
mv blog-to-publish/free-ai-humanizer-online.html blog/
sed -i '' 's/July 1, 2026/July 6, 2026/g' blog/free-ai-humanizer-online.html
git add .
git commit -m "Publish blog post 4/8: free-ai-humanizer-online (July 6)"
git push origin main
```

### 7月7日 — 第5篇
```bash
cd ~/Desktop/aitextcoach
mv blog-to-publish/how-to-make-ai-text-sound-human.html blog/
sed -i '' 's/July 5, 2026/July 7, 2026/g' blog/how-to-make-ai-text-sound-human.html
git add .
git commit -m "Publish blog post 5/8: how-to-make-ai-text-sound-human (July 7)"
git push origin main
```

### 7月8日 — 第6篇
```bash
cd ~/Desktop/aitextcoach
mv blog-to-publish/how-to-make-chatgpt-output-sound-human.html blog/
sed -i '' 's/July 3, 2026/July 8, 2026/g' blog/how-to-make-chatgpt-output-sound-human.html
git add .
git commit -m "Publish blog post 6/8: how-to-make-chatgpt-output-sound-human (July 8)"
git push origin main
```

### 7月9日 — 第7篇
```bash
cd ~/Desktop/aitextcoach
mv blog-to-publish/how-to-remove-ai-detection-from-text.html blog/
sed -i '' 's/July 2, 2026/July 9, 2026/g' blog/how-to-remove-ai-detection-from-text.html
git add .
git commit -m "Publish blog post 7/8: how-to-remove-ai-detection-from-text (July 9)"
git push origin main
```

### 7月10日 — 第8篇
```bash
cd ~/Desktop/aitextcoach
mv blog-to-publish/why-does-ai-writing-sound-robotic.html blog/
sed -i '' 's/July 4, 2026/July 10, 2026/g' blog/why-does-ai-writing-sound-robotic.html
git add .
git commit -m "Publish blog post 8/8: why-does-ai-writing-sound-robotic (July 10)"
git push origin main
```

---

*创建于 2026-07-05*
*作者：阿龙*
