#!/usr/bin/env python3
"""
FastAPI + MCP 템플릿 설정 스크립트
- 기존 템플릿 커스터마이징
- 백업 및 롤백 기능
"""
import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class TemplateSetup:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.backup_dir = project_path / ".template_backup"
        self.template_files = [
            "pyproject.toml",
            "README.md",
            ".cursor/mcp.json",
            "src/core/config.py",
            "src/core/models.py",
            "src/api/app.py",
            "src/mcp/server.py",
            "src/mcp/tools.py",
            "src/mcp/resources.py",
            "run_api_server.py",
            "run_mcp_server.py",
            "run_server.py",
            "run_docker.py",
            "Dockerfile",
            "docker-compose.yml",
            ".dockerignore",
            "examples/api_usage.py",
            "tests/test_api.py",
            "docs/TEMPLATE_GUIDE.md"
        ]

    def get_user_input(self, prompt: str, default: str = "") -> str:
        """사용자 입력을 받는 함수"""
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            return user_input if user_input else default
        return input(f"{prompt}: ").strip()

    def get_yes_no(self, prompt: str, default: bool = True) -> bool:
        """예/아니오 입력을 받는 함수"""
        default_str = "Y/n" if default else "y/N"
        while True:
            response = input(f"{prompt} [{default_str}]: ").strip().lower()
            if not response:
                return default
            if response in ['y', 'yes', '예']:
                return True
            if response in ['n', 'no', '아니오']:
                return False
            print("'y' 또는 'n'을 입력해주세요.")

    def create_backup(self) -> bool:
        """현재 템플릿 상태를 백업"""
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            
            self.backup_dir.mkdir(exist_ok=True)
            
            print("💾 현재 템플릿 상태를 백업합니다...")
            
            for file_path in self.template_files:
                source_file = self.project_path / file_path
                if source_file.exists():
                    backup_file = self.backup_dir / file_path
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, backup_file)
            
            # 메타데이터 저장
            metadata = {
                "backup_time": datetime.now().isoformat(),
                "original_files": [str(f) for f in self.template_files if (self.project_path / f).exists()]
            }
            
            with open(self.backup_dir / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 백업 완료: {self.backup_dir}")
            return True
            
        except Exception as e:
            print(f"❌ 백업 실패: {e}")
            return False

    def restore_backup(self) -> bool:
        """백업에서 복원"""
        try:
            if not self.backup_dir.exists():
                print("❌ 백업 파일이 없습니다.")
                return False
            
            metadata_file = self.backup_dir / "metadata.json"
            if not metadata_file.exists():
                print("❌ 백업 메타데이터가 없습니다.")
                return False
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            print("🔄 백업에서 복원합니다...")
            
            for file_path in metadata["original_files"]:
                backup_file = self.backup_dir / file_path
                target_file = self.project_path / file_path
                
                if backup_file.exists():
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup_file, target_file)
            
            print("✅ 복원 완료")
            return True
            
        except Exception as e:
            print(f"❌ 복원 실패: {e}")
            return False

    def replace_in_file(self, file_path: Path, replacements: Dict[str, str]) -> bool:
        """파일 내용에서 문자열 대치"""
        try:
            if not file_path.exists():
                return False
            
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            for old_text, new_text in replacements.items():
                content = content.replace(old_text, new_text)
            
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ 파일 수정 실패 {file_path}: {e}")
            return False

    def update_all_files(self, project_info: Dict[str, Any]) -> bool:
        """모든 파일에서 템플릿 정보를 프로젝트 정보로 대치"""
        
        # 기본 대치 맵핑
        replacements = {
            # 프로젝트 이름 관련
            "fastapi-mcp-template": project_info["name"],
            "FastAPI + MCP Template": project_info["title"],
            "FastAPI MCP Template": project_info["title"],
            
            # 설명 관련
            "FastAPI + MCP Template - 현대적인 API와 LLM 통합을 위한 개발 템플릿": project_info["description"],
            "**FastAPI**와 **MCP(Model Context Protocol)**를 결합한 개발 템플릿입니다.": project_info["description"],
            "현대적인 API 서버와 LLM 통합을 위한 MCP 서버를 동시에 제공하는 완전한 개발 환경을 제공합니다.": f"{project_info['description']} 프로젝트입니다.",
            
            # 작성자 관련
            'authors = ["Your Name <your.email@example.com>"]': f'authors = ["{project_info.get("author", "Your Name")} <{project_info.get("email", "your.email@example.com")}>"]',
            "Your Name": project_info.get("author", "Your Name"),
            "your.email@example.com": project_info.get("email", "your.email@example.com"),
            
            # 클래스/변수명 관련 (Python 식별자로 사용 가능한 형태)
            "FastApiMcpTemplate": self.to_pascal_case(project_info["name"]),
            "fastapi_mcp_template": self.to_snake_case(project_info["name"]),
            "FASTAPI_MCP_TEMPLATE": self.to_upper_snake_case(project_info["name"]),
            
            # Docker 관련 (컨테이너 이름)
            "fastapi-mcp-app": f"{self.to_snake_case(project_info['name'])}-app",
            "fastapi-mcp-dev": f"{self.to_snake_case(project_info['name'])}-dev",
            
            # 디렉토리/패키지명 관련
            "fastapi-mcp-template/": f"{project_info['name']}/",
            
            # 문서 관련
            "FastAPI + MCP 템플릿": project_info["title"],
            "템플릿": "프로젝트",
            
            # URL/도메인 관련 (예시)
            "fastapi-mcp-template.com": f"{project_info['name']}.com",
            "fastapi-mcp-template.example.com": f"{project_info['name']}.example.com",
        }
        
        print("🔄 프로젝트 파일들을 업데이트합니다...")
        
        updated_files = []
        
        for file_path in self.template_files:
            full_path = self.project_path / file_path
            if self.replace_in_file(full_path, replacements):
                updated_files.append(file_path)
        
        # 추가 파일들도 검사
        additional_files = [
            "setup_template.py",
            "scripts/setup_template.py",
            "scripts/init_blank_template.py"
        ]
        
        for file_path in additional_files:
            full_path = self.project_path / file_path
            if self.replace_in_file(full_path, replacements):
                updated_files.append(file_path)
        
        if updated_files:
            print("✅ 다음 파일들이 업데이트되었습니다:")
            for file_path in updated_files:
                print(f"   - {file_path}")
        else:
            print("ℹ️  업데이트할 파일이 없습니다.")
        
        return True

    def to_pascal_case(self, text: str) -> str:
        """kebab-case를 PascalCase로 변환"""
        return ''.join(word.capitalize() for word in text.replace('-', '_').split('_'))

    def to_snake_case(self, text: str) -> str:
        """kebab-case를 snake_case로 변환"""
        return text.replace('-', '_')

    def to_upper_snake_case(self, text: str) -> str:
        """kebab-case를 UPPER_SNAKE_CASE로 변환"""
        return text.replace('-', '_').upper()

    def move_template_files(self) -> bool:
        """템플릿 관련 파일들을 별도 폴더로 이동"""
        try:
            template_archive = self.project_path / ".template_archive"
            template_archive.mkdir(exist_ok=True)
            
            files_to_move = [
                "setup_template.py",
                "scripts/setup_template.py",
                "scripts/init_blank_template.py"
            ]
            
            moved_files = []
            
            for file_path in files_to_move:
                source_file = self.project_path / file_path
                if source_file.exists():
                    target_file = template_archive / file_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source_file), str(target_file))
                    moved_files.append(file_path)
            
            if moved_files:
                print(f"📁 템플릿 파일들을 {template_archive}로 이동했습니다:")
                for file_path in moved_files:
                    print(f"   - {file_path}")
                
                # 복원 스크립트 생성
                restore_script = template_archive / "restore_template.py"
                restore_code = f'''#!/usr/bin/env python3
"""
템플릿 파일 복원 스크립트
"""
import shutil
from pathlib import Path

def main():
    current_dir = Path(__file__).parent.parent
    archive_dir = Path(__file__).parent
    
    files_to_restore = {moved_files}
    
    print("🔄 템플릿 파일들을 복원합니다...")
    
    for file_path in files_to_restore:
        source_file = archive_dir / file_path
        target_file = current_dir / file_path
        
        if source_file.exists():
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(source_file), str(target_file))
            print(f"✅ 복원됨: {{file_path}}")
    
    print("✅ 복원 완료!")

if __name__ == "__main__":
    main()
'''
                restore_script.write_text(restore_code, encoding='utf-8')
                restore_script.chmod(0o755)
                
                print(f"📝 복원 스크립트 생성: {restore_script}")
            
            return True
            
        except Exception as e:
            print(f"❌ 파일 이동 실패: {e}")
            return False



    def customize_project(self) -> bool:
        """프로젝트 커스터마이징"""
        print("🚀 FastAPI + MCP 프로젝트 커스터마이징")
        print("=" * 50)
        
        # 백업 생성
        if not self.create_backup():
            return False
        
        # 프로젝트 정보 수집
        project_info = {}
        
        print("\n📝 프로젝트 정보를 입력해주세요:")
        project_info["name"] = self.get_user_input(
            "프로젝트 이름 (패키지명)", 
            "my-awesome-api"
        )
        
        project_info["title"] = self.get_user_input(
            "프로젝트 제목", 
            f"{project_info['name'].replace('-', ' ').title()}"
        )
        
        project_info["description"] = self.get_user_input(
            "프로젝트 설명",
            f"{project_info['title']} - FastAPI와 MCP를 활용한 API 서버"
        )
        
        project_info["author"] = self.get_user_input("작성자 이름", "")
        if project_info["author"]:
            project_info["email"] = self.get_user_input("작성자 이메일", "")
        
        # 확인
        print(f"\n📋 설정 요약:")
        print(f"  - 프로젝트명: {project_info['name']}")
        print(f"  - 제목: {project_info['title']}")
        print(f"  - 설명: {project_info['description']}")
        if project_info.get("author"):
            print(f"  - 작성자: {project_info['author']}")
            if project_info.get("email"):
                print(f"  - 이메일: {project_info['email']}")
        
        if not self.get_yes_no("\n✅ 위 설정으로 프로젝트를 커스터마이징하시겠습니까?", True):
            print("❌ 커스터마이징이 취소되었습니다.")
            return False
        
        # 파일 업데이트
        if not self.update_all_files(project_info):
            return False
        
        # 템플릿 파일 정리
        if self.get_yes_no("\n🧹 템플릿 관련 파일들을 정리하시겠습니까?", True):
            self.move_template_files()
        
        print("\n🎉 프로젝트 커스터마이징이 완료되었습니다!")
        print("\n📚 다음 단계:")
        print("1. uv sync - 의존성 설치")
        print("2. python run_server.py - 서버 실행")
        print("3. 코드 수정 및 개발 시작")
        
        print("\n🔄 롤백 방법:")
        print(f"python -c \"from pathlib import Path; from setup_template import TemplateSetup; TemplateSetup(Path('.')).restore_backup()\"")
        
        return True


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="FastAPI + MCP 템플릿 설정 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python setup_template.py --customize                    # 현재 템플릿 커스터마이징
  python setup_template.py --restore                      # 백업에서 복원
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--customize",
        action="store_true",
        help="현재 템플릿을 커스터마이징"
    )

    group.add_argument(
        "--restore",
        action="store_true",
        help="백업에서 복원"
    )
    

    
    args = parser.parse_args()
    
    current_path = Path.cwd()
    setup = TemplateSetup(current_path)
    
    try:
        if args.customize:
            # 현재 템플릿 커스터마이징
            if not (current_path / "pyproject.toml").exists():
                print("❌ 오류: 템플릿 루트 디렉토리에서 실행해주세요.")
                sys.exit(1)
            
            success = setup.customize_project()
            
        
        elif args.restore:
            # 백업에서 복원
            print("🔄 백업에서 복원")
            print("=" * 50)
            success = setup.restore_backup()
        
        if success:
            print("\n✅ 작업이 성공적으로 완료되었습니다!")
        else:
            print("\n❌ 작업이 실패했습니다.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ 사용자에 의해 취소되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 