#!/usr/bin/env python3
"""
Docker를 사용하여 FastAPI + MCP 서버 실행

이 스크립트는 Docker Compose를 사용하여 
FastAPI 서버와 MCP 서버를 컨테이너에서 실행합니다.
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional


class DockerRunner:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.compose_file = project_path / "docker-compose.yml"
        self.dockerfile = project_path / "Dockerfile"

    def check_docker(self) -> bool:
        """Docker가 설치되어 있고 실행 중인지 확인"""
        try:
            # Docker 데몬 확인
            result = subprocess.run(
                ["docker", "info"], 
                capture_output=True, 
                text=True
            )
            if result.returncode != 0:
                print("❌ Docker 데몬이 실행되고 있지 않습니다.")
                print("Docker Desktop을 시작하거나 Docker 서비스를 시작해주세요.")
                return False
            
            # Docker Compose 확인
            result = subprocess.run(
                ["docker", "compose", "version"], 
                capture_output=True, 
                text=True
            )
            if result.returncode != 0:
                print("❌ Docker Compose를 찾을 수 없습니다.")
                print("Docker Compose를 설치해주세요.")
                return False
            
            return True
            
        except FileNotFoundError:
            print("❌ Docker를 찾을 수 없습니다.")
            print("Docker를 설치해주세요: https://docs.docker.com/get-docker/")
            return False

    def check_files(self) -> bool:
        """필요한 파일들이 존재하는지 확인"""
        missing_files = []
        
        if not self.dockerfile.exists():
            missing_files.append("Dockerfile")
        
        if not self.compose_file.exists():
            missing_files.append("docker-compose.yml")
        
        if not (self.project_path / "pyproject.toml").exists():
            missing_files.append("pyproject.toml")
        
        if missing_files:
            print(f"❌ 다음 파일들이 없습니다: {', '.join(missing_files)}")
            return False
        
        return True

    def run_command(self, cmd: List[str], capture_output: bool = False) -> subprocess.CompletedProcess:
        """Docker 명령어 실행"""
        print(f"🔧 실행: {' '.join(cmd)}")
        
        if capture_output:
            return subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_path)
        else:
            return subprocess.run(cmd, cwd=self.project_path)

    def build_image(self, no_cache: bool = False) -> bool:
        """Docker 이미지 빌드"""
        print("🏗️  Docker 이미지를 빌드합니다...")
        
        cmd = ["docker", "compose", "build"]
        if no_cache:
            cmd.append("--no-cache")
        
        result = self.run_command(cmd)
        
        if result.returncode == 0:
            print("✅ 이미지 빌드 완료")
            return True
        else:
            print("❌ 이미지 빌드 실패")
            return False

    def start_services(self, dev_mode: bool = False, detach: bool = True) -> bool:
        """서비스 시작"""
        print("🚀 서비스를 시작합니다...")
        
        cmd = ["docker", "compose"]
        
        if dev_mode:
            cmd.extend(["--profile", "dev"])
        
        cmd.append("up")
        
        if detach:
            cmd.append("-d")
        
        result = self.run_command(cmd)
        
        if result.returncode == 0:
            if detach:
                print("✅ 서비스가 백그라운드에서 시작되었습니다.")
                self.show_status()
            return True
        else:
            print("❌ 서비스 시작 실패")
            return False

    def stop_services(self) -> bool:
        """서비스 중지"""
        print("🛑 서비스를 중지합니다...")
        
        result = self.run_command(["docker", "compose", "down"])
        
        if result.returncode == 0:
            print("✅ 서비스가 중지되었습니다.")
            return True
        else:
            print("❌ 서비스 중지 실패")
            return False

    def restart_services(self, dev_mode: bool = False) -> bool:
        """서비스 재시작"""
        print("🔄 서비스를 재시작합니다...")
        
        self.stop_services()
        time.sleep(2)
        return self.start_services(dev_mode=dev_mode)

    def show_logs(self, follow: bool = False, service: Optional[str] = None) -> None:
        """로그 표시"""
        cmd = ["docker", "compose", "logs"]
        
        if follow:
            cmd.append("-f")
        
        if service:
            cmd.append(service)
        
        self.run_command(cmd)

    def show_status(self) -> None:
        """서비스 상태 표시"""
        print("\n📊 서비스 상태:")
        result = self.run_command(["docker", "compose", "ps"], capture_output=True)
        
        if result.returncode == 0:
            print(result.stdout)
        
        print("\n🌐 접속 정보:")
        print("  - FastAPI 서버: http://localhost:8000")
        print("  - API 문서: http://localhost:8000/docs")
        print("  - MCP SSE 서버: http://localhost:8001/sse")
        print("  - 헬스체크: http://localhost:8000/health")

    def exec_shell(self, service: str = "fastapi-mcp-app") -> None:
        """컨테이너 내부 쉘 접속"""
        print(f"🐚 {service} 컨테이너에 접속합니다...")
        
        cmd = ["docker", "compose", "exec", service, "/bin/bash"]
        self.run_command(cmd)

    def cleanup(self) -> bool:
        """리소스 정리"""
        print("🧹 Docker 리소스를 정리합니다...")
        
        # 컨테이너 중지 및 제거
        self.run_command(["docker", "compose", "down", "--volumes", "--remove-orphans"])
        
        # 이미지 제거 (선택사항)
        result = self.run_command(
            ["docker", "images", "-q", "fastapi-mcp-template"], 
            capture_output=True
        )
        
        if result.stdout.strip():
            self.run_command(["docker", "rmi", result.stdout.strip()])
        
        print("✅ 정리 완료")
        return True


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="Docker를 사용하여 FastAPI + MCP 서버 실행",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python run_docker.py --start                    # 서비스 시작 (백그라운드)
  python run_docker.py --start --foreground       # 서비스 시작 (포그라운드)
  python run_docker.py --start --dev              # 개발 모드로 시작
  python run_docker.py --build --start            # 빌드 후 시작
  python run_docker.py --logs --follow            # 로그 실시간 모니터링
  python run_docker.py --stop                     # 서비스 중지
  python run_docker.py --restart                  # 서비스 재시작
  python run_docker.py --shell                    # 컨테이너 쉘 접속
  python run_docker.py --status                   # 상태 확인
  python run_docker.py --cleanup                  # 리소스 정리
        """
    )
    
    # 액션 그룹
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--start", 
        action="store_true", 
        help="서비스 시작"
    )
    action_group.add_argument(
        "--stop", 
        action="store_true", 
        help="서비스 중지"
    )
    action_group.add_argument(
        "--restart", 
        action="store_true", 
        help="서비스 재시작"
    )
    action_group.add_argument(
        "--logs", 
        action="store_true", 
        help="로그 표시"
    )
    action_group.add_argument(
        "--status", 
        action="store_true", 
        help="서비스 상태 확인"
    )
    action_group.add_argument(
        "--shell", 
        action="store_true", 
        help="컨테이너 쉘 접속"
    )
    action_group.add_argument(
        "--cleanup", 
        action="store_true", 
        help="Docker 리소스 정리"
    )
    
    # 옵션
    parser.add_argument(
        "--build", 
        action="store_true", 
        help="이미지 빌드"
    )
    parser.add_argument(
        "--no-cache", 
        action="store_true", 
        help="캐시 없이 빌드"
    )
    parser.add_argument(
        "--dev", 
        action="store_true", 
        help="개발 모드 (포트 8002, 8003 사용)"
    )
    parser.add_argument(
        "--foreground", 
        action="store_true", 
        help="포그라운드에서 실행 (로그 실시간 표시)"
    )
    parser.add_argument(
        "--follow", 
        action="store_true", 
        help="로그 실시간 모니터링"
    )
    parser.add_argument(
        "--service", 
        choices=["fastapi-mcp-app", "fastapi-mcp-dev"],
        help="특정 서비스 대상"
    )
    
    args = parser.parse_args()
    
    # 기본 액션 설정
    if not any([args.start, args.stop, args.restart, args.logs, args.status, args.shell, args.cleanup]):
        if args.build:
            args.start = True  # 빌드 후 시작
        else:
            args.status = True  # 기본적으로 상태 확인
    
    current_path = Path.cwd()
    runner = DockerRunner(current_path)
    
    try:
        # 사전 검사
        if not runner.check_docker():
            sys.exit(1)
        
        if not runner.check_files():
            sys.exit(1)
        
        success = True
        
        # 빌드
        if args.build:
            success = runner.build_image(no_cache=args.no_cache)
            if not success:
                sys.exit(1)
        
        # 액션 실행
        if args.start:
            success = runner.start_services(
                dev_mode=args.dev, 
                detach=not args.foreground
            )
            
        elif args.stop:
            success = runner.stop_services()
            
        elif args.restart:
            success = runner.restart_services(dev_mode=args.dev)
            
        elif args.logs:
            runner.show_logs(follow=args.follow, service=args.service)
            
        elif args.status:
            runner.show_status()
            
        elif args.shell:
            service = args.service or "fastapi-mcp-app"
            runner.exec_shell(service)
            
        elif args.cleanup:
            success = runner.cleanup()
        
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ 사용자에 의해 취소되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 