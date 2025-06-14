# 🚀 FindYourTab Setup Commands

## **STEP 1: Initialize Git Repository**

```bash
git init
git add .
git commit -m "Initial commit: FindYourTab application with executable and GitHub Pages"
```

## **STEP 2: Create GitHub Repository**

1. Go to https://github.com/new
2. Repository name: `findyourtab`
3. Description: `Universal Browser Tab Manager for Windows`
4. Make it **Public**
5. Click **Create repository**

## **STEP 3: Push to GitHub**

```bash
git branch -M main
git remote add origin https://github.com/YOURUSERNAME/findyourtab.git
git push -u origin main
```

**⚠️ Replace `YOURUSERNAME` with your actual GitHub username!**

## **STEP 4: Enable GitHub Pages**

1. Go to your repository on GitHub
2. Click **Settings** tab
3. Scroll down to **Pages** in the left sidebar
4. Under **Source**, select **Deploy from a branch**
5. Branch: **main**
6. Folder: **/ (root)** → Change to **docs**
7. Click **Save**

Your website will be live at: `https://YOURUSERNAME.github.io/findyourtab/`

## **STEP 5: Create Your First Release**

```bash
git tag v1.0.0
git push origin v1.0.0
```

This will trigger GitHub Actions to:
- ✅ Build the executable automatically
- ✅ Create a GitHub release
- ✅ Upload the executable for download

## **STEP 6: Update Website Links**

After the release is created:

1. Edit `docs/index.html`
2. Replace all instances of `yourusername` with your GitHub username
3. Update the Chrome Web Store link when you publish the extension

```bash
git add docs/index.html
git commit -m "Update website links with actual GitHub username"
git push
```

## **STEP 7: Test Everything**

1. **Check your website**: `https://YOURUSERNAME.github.io/findyourtab/`
2. **Check the release**: `https://github.com/YOURUSERNAME/findyourtab/releases`
3. **Download and test the executable**
4. **Test the browser extension**

## **🎉 You're Done!**

Your FindYourTab project is now:
- ✅ **Live website** for users to download
- ✅ **Automatic executable building** via GitHub Actions
- ✅ **Professional presentation** with modern UI
- ✅ **Easy distribution** through GitHub releases

## **📋 Quick Checklist**

- [ ] Created GitHub repository
- [ ] Pushed code to GitHub
- [ ] Enabled GitHub Pages (docs folder)
- [ ] Created first release tag (v1.0.0)
- [ ] Verified website is live
- [ ] Verified executable downloads
- [ ] Updated all username placeholders
- [ ] Tested the application end-to-end

## **🔄 For Future Releases**

```bash
# Update version numbers in files, then:
git add .
git commit -m "Version 1.1.0: Add new features"
git tag v1.1.0
git push origin main
git push origin v1.1.0
```

## **🆘 Need Help?**

- **GitHub Pages not working?** Check Settings → Pages
- **Actions failing?** Check the Actions tab for error logs
- **Executable not working?** Test locally with `python build_executable.py`
- **Website broken?** Validate HTML and check browser console

---

**🎯 Your project is ready for users! Share the website link and start getting feedback!** 