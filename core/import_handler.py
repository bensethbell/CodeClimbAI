"""
Import dependency detection and handling for CodeClimbAI.
Extracted from session_manager.py to improve modularity and reduce file size.
"""
import re
from typing import List


class ImportHandler:
    """Handles detection and management of external dependencies that may not be available."""
    
    # Common packages that might not be available in Streamlit Cloud
    UNAVAILABLE_PACKAGES = {
        'selenium', 'webdriver', 'chromedriver_binary', 'geckodriver_autoinstaller',
        'cv2', 'opencv', 'torch', 'tensorflow', 'keras', 'scrapy', 'requests_html',
        'pyautogui', 'pynput', 'keyboard', 'mouse', 'win32api', 'win32gui',
        'psutil', 'subprocess', 'multiprocessing', 'threading', 'asyncio',
        'tkinter', 'PyQt5', 'PyQt6', 'kivy', 'pygame'
    }
    
    # Package purpose descriptions for user-friendly messaging
    PACKAGE_PURPOSES = {
        'selenium': 'web automation and testing',
        'cv2': 'computer vision and image processing',
        'torch': 'deep learning and neural networks',
        'tensorflow': 'machine learning and AI',
        'scrapy': 'web scraping',
        'tkinter': 'desktop GUI applications',
        'pygame': 'game development',
        'requests_html': 'web scraping with JavaScript support',
        'pyautogui': 'desktop automation',
        'psutil': 'system monitoring',
        'keyboard': 'keyboard automation',
        'mouse': 'mouse automation',
        'pynput': 'input automation',
        'asyncio': 'asynchronous programming'
    }
    
    @classmethod
    def detect_unavailable_imports(cls, code: str) -> List[str]:
        """
        Detect external dependencies in code that might not be available in Streamlit Cloud.
        
        Args:
            code: Python code to analyze
            
        Returns:
            List of unavailable package names found in the code
        """
        # Find import statements using regex patterns
        import_patterns = [
            r'from\s+(\w+)',      # from package
            r'import\s+(\w+)',    # import package  
            r'from\s+(\w+)\.',    # from package.module
            r'import\s+(\w+)\.'   # import package.module
        ]
        
        found_unavailable = []
        for pattern in import_patterns:
            matches = re.findall(pattern, code, re.MULTILINE)
            for match in matches:
                if match in cls.UNAVAILABLE_PACKAGES:
                    found_unavailable.append(match)
        
        return list(set(found_unavailable))  # Remove duplicates
    
    @classmethod
    def get_package_purpose(cls, package_name: str) -> str:
        """
        Get a human-readable description of what a package is used for.
        
        Args:
            package_name: Name of the package
            
        Returns:
            Human-readable purpose description
        """
        return cls.PACKAGE_PURPOSES.get(package_name, 'specialized tasks')
    
    @classmethod
    def is_import_error(cls, error_message: str, detected_packages: List[str]) -> bool:
        """
        Check if an execution error is due to missing import dependencies.
        
        Args:
            error_message: The error message from code execution
            detected_packages: List of unavailable packages detected in the code
            
        Returns:
            True if the error is likely due to missing imports
        """
        error_text = error_message.lower()
        return any(pkg in error_text for pkg in detected_packages)
    
    @classmethod
    def create_import_limitation_message(cls, detected_packages: List[str]) -> str:
        """
        Create a user-friendly message explaining import limitations.
        
        Args:
            detected_packages: List of unavailable packages detected
            
        Returns:
            Formatted message explaining the limitation
        """
        if not detected_packages:
            return ""
        
        main_package = detected_packages[0]
        purpose = cls.get_package_purpose(main_package)
        
        if len(detected_packages) == 1:
            return f"I notice you're using `{main_package}` - that's great for {purpose}! While I can't run this code in my environment ({main_package} isn't installed here), **I can still help you optimize the code structure and patterns**."
        else:
            package_list = ', '.join(detected_packages)
            return f"I notice you're using `{package_list}` - great for {purpose} and related tasks! While I can't run this code in my environment (those packages aren't installed here), **I can still help you optimize the code structure and patterns**."
