# FindYourTab Deployment Guide

## 🚀 Complete Setup Process

### Step 1: GitHub Repository Setup

1. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: FindYourTab application"
   git branch -M main
   git remote add origin https://github.com/yourusername/findyourtab.git
   git push -u origin main
   ```

2. **Enable GitHub Pages**
   - Go to your repository on GitHub
   - Click **Settings** → **Pages**
   - Source: **Deploy from a branch**
   - Branch: **main** → **/ (root)** → **docs**
   - Click **Save**
   - Your site will be available at: `https://yourusername.github.io/findyourtab/`

### Step 2: Automatic Executable Building

The GitHub Actions workflow will automatically:
- Build the executable when you push a version tag
- Create a GitHub release with the executable
- Update the download links on your website

**To create a release:**
```bash
git tag v1.0.0
git push origin v1.0.0
```

### Step 3: Manual Executable Building (Local)

If you want to build locally:

```bash
cd python
python build_executable.py
```

The executable will be created in `python/dist/FindYourTab.exe`

### Step 4: Update Website Links

After your first release, update the download links in `docs/index.html`:

1. Replace `yourusername` with your actual GitHub username
2. Update the Chrome Web Store link with your extension ID
3. Update version numbers and file sizes as needed

### Step 5: Browser Extension Distribution

#### Chrome Web Store
1. Zip the `public/` directory contents
2. Upload to Chrome Web Store Developer Dashboard
3. Update the website with the Chrome Web Store link

#### Manual Installation (Development)
Users can load the unpacked extension:
1. Open Chrome → Extensions → Developer mode
2. Click "Load unpacked"
3. Select the `public/` folder

## 📁 File Structure

```
findyourtab/
├── docs/                    # GitHub Pages website
│   └── index.html          # Landing page
├── python/                 # Desktop application
│   ├── findyourtab_native.py
│   ├── build_executable.py
│   ├── requirements.txt
│   └── dist/              # Built executable (after build)
├── public/                # Browser extension
│   ├── manifest.json
│   ├── popup.html
│   └── static/
├── .github/
│   └── workflows/
│       └── build-release.yml
└── DEPLOYMENT_GUIDE.md
```

## 🔧 Configuration Checklist

### Before First Release:

- [ ] Update GitHub username in all files
- [ ] Test executable builds locally
- [ ] Verify browser extension works
- [ ] Update version numbers
- [ ] Test GitHub Pages deployment
- [ ] Create Chrome Web Store listing

### For Each Release:

- [ ] Update version in `build_executable.py`
- [ ] Update version in `docs/index.html`
- [ ] Update version in `manifest.json`
- [ ] Test all functionality
- [ ] Create git tag: `git tag v1.x.x`
- [ ] Push tag: `git push origin v1.x.x`
- [ ] Verify GitHub Actions build
- [ ] Update Chrome Web Store

## 🌐 Website Customization

### Update Branding
- Change colors in CSS variables
- Update logo and favicon
- Modify feature descriptions
- Add screenshots/GIFs

### Analytics (Optional)
Add Google Analytics or similar:
```html
<!-- Add to <head> in docs/index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🐛 Troubleshooting

### GitHub Actions Fails
- Check Python dependencies in `requirements.txt`
- Verify PyInstaller compatibility
- Check Windows-specific paths

### GitHub Pages Not Loading
- Ensure `docs/` folder is in main branch
- Check GitHub Pages settings
- Verify HTML syntax

### Executable Issues
- Test on clean Windows machine
- Check antivirus false positives
- Verify all dependencies included

### Extension Issues
- Test manifest.json validity
- Check Chrome Web Store policies
- Verify all permissions justified

## 📊 Success Metrics

Track these metrics for your project:
- GitHub Stars/Forks
- Download counts from releases
- Chrome Web Store users
- GitHub Issues/Feedback
- Website traffic (if analytics enabled)

## 🔄 Maintenance

### Regular Updates
- Monitor for security vulnerabilities
- Update Python dependencies
- Test with new browser versions
- Respond to user feedback

### Version Numbering
- Major: Breaking changes (v2.0.0)
- Minor: New features (v1.1.0)
- Patch: Bug fixes (v1.0.1)

---

## 🎉 You're Ready!

Your FindYourTab project is now set up for:
- ✅ Automatic executable building
- ✅ Professional website
- ✅ Easy distribution
- ✅ User-friendly installation

**Next Steps:**
1. Push to GitHub
2. Enable GitHub Pages
3. Create your first release tag
4. Share with users!

Good luck with your project! 🚀 