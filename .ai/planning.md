# Quba (큐베) 프로젝트 기획서

## 서비스 개요
**Quba**는 Entry Python을 위한 종합 AI 서비스 플랫폼으로, 교육용 프로그래밍 언어에 특화된 AI 도구들을 제공합니다.

## 전제 조건
1. **Entry**: 한국형 스크래치 (교육용 블록형 프로그래밍 언어)
2. **Entry Python**: Entry와 변환 가능한 Python 기반 교육용 프로그래밍 언어

## 핵심 서비스
Entry Python을 위한 모든 AI Set 모음 - 교육용 프로그래밍 언어에 붙는 AI Wrapper + Helper + MCP + 기타 가능한 모든 AI 기능

## 주요 기능

### 1. Entry RAG 시스템
- **목적**: Entry 관련 정보의 효율적 검색 및 활용
- **기능**: AWS 서비스에 Entry 관련 정보를 임베딩하여 지식 베이스 구축
- **활용**: 학습자 질문에 대한 정확한 답변 제공

### 2. Entry Language MCP
- **목적**: Entry 정보 쿼리 인터페이스 제공
- **기능**: Entry 관련 정보를 효율적으로 쿼리할 수 있는 MCP 서비스
- **활용**: 다양한 AI 도구들이 Entry 정보에 접근 가능

### 3. Entry 학습 챗봇
- **목적**: 개인화된 Entry 학습 지원
- **기능**: Entry 학습을 위한 대화형 AI 튜터
- **활용**: 실시간 질답, 학습 가이드, 코드 리뷰

### 4. Entry Studio MCP
- **목적**: Entry Studio 자동화 및 조작
- **기능**: 
  - 1차: Entry Studio (일렉트론 기반) 조작 MCP
  - 2차: 웹 기반 Entry Studio 셀레늄 조작 (코드 수정 가능)
- **활용**: 자동 코드 생성, 프로젝트 관리, 디버깅 지원

## 기술 아키텍처
- **프론트엔드**: Entry Studio 통합
- **백엔드**: AWS 기반 마이크로서비스
- **AI/ML**: RAG, MCP, 챗봇 서비스
- **데이터**: Entry 관련 지식 베이스

## 타겟 사용자
- Entry/Entry Python 학습자
- 교육자 및 강사
- 교육 콘텐츠 개발자
- 프로그래밍 교육 기관