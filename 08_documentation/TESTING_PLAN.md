# Testing Plan for Repository Reorganization

## 🧪 **Testing Strategy**

This document outlines the testing plan for the repository reorganization changes before merging back to main.

## 📋 **Pre-Merge Testing Checklist**

### **1. Environment Setup Testing**
```bash
# Test environment setup
python 01_environment/setup_environment.py

# Verify virtual environment creation
# Check dependencies installation
# Verify environment variables
```

### **2. System Testing**
```bash
# Run comprehensive system tests
python 06_testing/test_system.py

# Expected results:
# - All tests should pass
# - No missing dependencies
# - All components accessible
```

### **3. Interactive Launcher Testing**
```bash
# Test the main launcher
python 10_scripts/launch_london_llm.py

# Test each menu option:
# 1. Environment setup
# 2. Data collection
# 3. Tokenizer training
# 4. Model training
# 5. Model evaluation
# 6. System testing
# 7. Complete pipeline
# 8. System status
# 9. Help & documentation
```

### **4. Individual Component Testing**

#### **Data Collection**
```bash
cd 02_data_collection
python download_historical_data.py --help
# Test with small dataset first
```

#### **Tokenizer Training**
```bash
cd 03_tokenizer
python train_tokenizer.py --help
# Test with sample data
```

#### **Model Training**
```bash
cd 04_training
python train_model.py --help
# Test configuration loading
```

#### **Model Evaluation**
```bash
cd 05_evaluation
python evaluate_model.py --help
# Test evaluation framework
```

### **5. Documentation Testing**
- [ ] All README files load correctly
- [ ] Links work properly
- [ ] Code examples are accurate
- [ ] File paths are correct

### **6. File Structure Validation**
```bash
# Verify all expected files exist
ls -la 01_environment/
ls -la 02_data_collection/
ls -la 03_tokenizer/
ls -la 04_training/
ls -la 05_evaluation/
ls -la 06_testing/
ls -la 07_utilities/
ls -la 08_documentation/
ls -la 09_models/
ls -la 10_scripts/
```

## 🔍 **Testing Commands**

### **Quick Test Script**
```bash
#!/bin/bash
# quick_test.sh

echo "🧪 Testing Repository Reorganization"
echo "=================================="

# Test 1: System tests
echo "1. Running system tests..."
python 06_testing/test_system.py
if [ $? -eq 0 ]; then
    echo "✅ System tests passed"
else
    echo "❌ System tests failed"
    exit 1
fi

# Test 2: Launcher
echo "2. Testing launcher..."
python 10_scripts/launch_london_llm.py --step status
if [ $? -eq 0 ]; then
    echo "✅ Launcher works"
else
    echo "❌ Launcher failed"
    exit 1
fi

# Test 3: File structure
echo "3. Checking file structure..."
expected_dirs=("01_environment" "02_data_collection" "03_tokenizer" "04_training" "05_evaluation" "06_testing" "07_utilities" "08_documentation" "09_models" "10_scripts")
for dir in "${expected_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir exists"
    else
        echo "❌ $dir missing"
        exit 1
    fi
done

echo "🎉 All tests passed! Ready for merge."
```

## 🚨 **Known Issues to Watch For**

### **Potential Issues**
1. **Import Paths**: Some scripts might have hardcoded paths
2. **Dependencies**: New scripts might need additional packages
3. **File Permissions**: Shell scripts might need execute permissions
4. **Environment Variables**: Paths might need updating

### **Mitigation**
- All scripts use relative paths
- Dependencies are in requirements.txt
- Shell scripts have proper permissions
- Environment setup handles path configuration

## 📊 **Success Criteria**

### **Must Pass**
- [ ] System tests run without errors
- [ ] Launcher starts and shows menu
- [ ] All directories exist and are accessible
- [ ] Documentation loads correctly
- [ ] No broken imports or missing files

### **Should Pass**
- [ ] Individual components can be run
- [ ] Help commands work for all scripts
- [ ] File structure is clean and logical
- [ ] All functionality preserved

## 🔄 **Rollback Plan**

If issues are found:
```bash
# Switch back to dev branch
git checkout dev

# Create hotfix branch
git checkout -b hotfix/reorganization-issues

# Fix issues
# Test fixes
# Merge back to dev
```

## 📝 **Testing Results Template**

```
Testing Results for Repository Reorganization
============================================

Date: [DATE]
Tester: [NAME]
Branch: feature/repository-reorganization

Environment:
- OS: [OS]
- Python: [VERSION]
- Git: [VERSION]

Test Results:
- System Tests: [PASS/FAIL]
- Launcher: [PASS/FAIL]
- File Structure: [PASS/FAIL]
- Documentation: [PASS/FAIL]
- Individual Components: [PASS/FAIL]

Issues Found:
- [List any issues]

Recommendations:
- [List recommendations]

Overall Status: [READY FOR MERGE/NEEDS FIXES]
```

## 🎯 **Next Steps After Testing**

1. **If All Tests Pass**:
   - Merge to dev branch
   - Test on dev branch
   - Merge to main
   - Create release tag

2. **If Issues Found**:
   - Fix issues on feature branch
   - Re-test
   - Repeat until all tests pass

3. **After Successful Merge**:
   - Update main README
   - Create release notes
   - Notify team of changes
