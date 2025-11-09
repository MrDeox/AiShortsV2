import json
import logging
import base64
from typing import List, Optional, Dict, Any
from pathlib import Path
import cv2


class BrollQueryService:
    """Responsável por gerar queries de B-roll usando modelos LLM."""

    def __init__(self, llm_client, max_tokens: int = 200, temperature: float = 0.3):
        self._llm_client = llm_client
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._logger = logging.getLogger(self.__class__.__name__)

    def generate_queries(self, script_text: Optional[str]) -> List[str]:
        """Gera queries curtas e acionáveis para busca de B-roll."""
        if not script_text:
self._logger.debug("Texto do script vazio; sem queries de B-roll para gerar.")
            return []

        system_message = (
            "You are a video content assistant. Your job is to read the provided short-form script "
            "and output concise YouTube search queries (in English) to find matching b-roll footage. "
            "Return 3 to 5 queries, 3-5 words each, focused on nouns and visual actions. "
            "Output them as a JSON array of strings with no explanations."
        )
        prompt = (
            "Script:\n"
            f"{script_text}\n\n"
            "Return JSON array with search queries."
        )

        try:
            response = self._llm_client.generate_content(
                prompt=prompt,
                system_message=system_message,
                max_tokens=self._max_tokens,
                temperature=self._temperature
            )
        except Exception as error:
self._logger.warning("Falha na chamada LLM para queries de B-roll: %s", error)
            return []

        raw_content = (response.content or "").strip()
        if not raw_content:
self._logger.info("LLM retornou resposta vazia para queries de B-roll.")
            return []

        queries: List[str] = []
        try:
            parsed = json.loads(raw_content)
            if isinstance(parsed, list):
                queries = [str(item).strip() for item in parsed if str(item).strip()]
            else:
                raise ValueError("Resposta não era um array JSON.")
        except Exception:
            queries = [
                line.strip("-• ").strip()
                for line in raw_content.splitlines()
                if line.strip()
            ]

        deduped = []
        for query in queries:
            if query and query not in deduped:
                deduped.append(query)

        final_queries = deduped[:5]
self._logger.info("Queries de B-roll geradas: %s", final_queries)
        return final_queries
    
    def enhance_queries_with_scene_detection(self, 
                                            script_text: Optional[str],
                                            video_frames: Optional[List[str]] = None,
                                            video_metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Gera queries de B-roll avançadas usando scene detection com LLM multimodal.
        
        Args:
            script_text: Script do vídeo
            video_frames: Lista de paths para frames de vídeo (para análise visual)
            video_metadata: Metadados dos vídeos candidatos
            
        Returns:
            Lista enhanced de queries de B-roll
        """
        if not script_text:
            return self.generate_queries(script_text)
        
        # Analisar frames se disponíveis (LLM multimodal)
        frame_analysis = ""
        if video_frames and len(video_frames) > 0:
            frame_analysis = self._analyze_video_frames(video_frames[:3])  # Limitar a 3 frames
        
        system_message = (
            "You are an expert video content strategist with multimodal analysis capabilities. "
            "Analyze the script and video frames to generate HIGHLY TARGETED b-roll search queries. "
            "Focus on: 1) Visual emotional impact, 2) Scene relevance, 3) Audience engagement. "
            "Return 5-7 queries, 3-6 words each, in JSON array format. "
            "Think about what visual moments would create maximum impact."
        )
        
        prompt = f"""
SCRIPT ANALYSIS:
{script_text}

{'FRAME ANALYSIS:' + frame_analysis if frame_analysis else ''}

VIDEO METADATA:
{json.dumps(video_metadata or {}, indent=2) if video_metadata else 'No metadata available'}

TASK: Generate 5-7 highly targeted b-roll search queries that would:
- Create emotional connection with viewers
- Match the visual tone of the content
- Drive engagement and sharing
- Be searchable on YouTube

Return JSON array: ["query1", "query2", ...]
"""
        
        try:
            response = self._llm_client.generate_content(
                prompt=prompt,
                system_message=system_message,
                max_tokens=400,
                temperature=0.4
            )
            
            raw_content = (response.content or "").strip()
            if not raw_content:
                return self.generate_queries(script_text)
            
            # Parse JSON response
            try:
                parsed = json.loads(raw_content)
                if isinstance(parsed, list):
                    enhanced_queries = [str(item).strip() for item in parsed if str(item).strip()]
self._logger.info(f" Enhanced queries geradas: {enhanced_queries}")
                    return enhanced_queries[:7]
            except json.JSONDecodeError:
self._logger.warning("Falha ao parsear JSON de enhanced queries, usando fallback")
            
        except Exception as e:
self._logger.warning(f"Falha na enhanced query generation: {e}")
        
        # Fallback para método original
        return self.generate_queries(script_text)
    
    def _analyze_video_frames(self, frame_paths: List[str]) -> str:
        """
        Analisa frames de vídeo usando LLM multimodal.
        
        Args:
            frame_paths: Lista de paths para frames de vídeo
            
        Returns:
            Análise visual em texto
        """
        frame_descriptions = []
        
        for i, frame_path in enumerate(frame_paths):
            try:
                if not Path(frame_path).exists():
                    continue
                    
                # Ler e codificar frame
                with open(frame_path, 'rb') as f:
                    frame_data = f.read()
                    frame_base64 = base64.b64encode(frame_data).decode('utf-8')
                
                # Criar prompt para análise visual
                vision_prompt = f"""
Analyze this video frame #{i+1} and describe:
1. Visual content (objects, people, environment)
2. Mood and emotional tone
3. Color palette and lighting
4. Composition and camera angles
5. Movement or action present

Provide a concise visual analysis for b-roll matching.
"""
                
                # Fazer análise com o LLM (usando formato de imagem)
                response = self._llm_client.generate_content(
                    prompt=vision_prompt,
                    max_tokens=200,
                    temperature=0.2
                )
                
                if response.content:
                    frame_descriptions.append(f"Frame {i+1}: {response.content.strip()}")
                    
            except Exception as e:
self._logger.warning(f"Erro ao analisar frame {frame_path}: {e}")
                continue
        
        return "\n\n".join(frame_descriptions) if frame_descriptions else "Frame analysis unavailable"
    
    def suggest_video_modifications(self, 
                                  video_path: str,
                                  target_mood: str,
                                  script_context: str) -> Dict[str, Any]:
        """
        Sugere modificações no vídeo baseado na análise visual LLM.
        
        Args:
            video_path: Path do vídeo
            target_mood: Mood desejado (dramatic, uplifting, mysterious, etc)
            script_context: Contexto do script
            
        Returns:
            Sugestões de modificação
        """
        try:
            # Extrair alguns frames do vídeo
            frames = self._extract_frames_from_video(video_path, num_frames=3)
            if not frames:
                return {"error": "Could not extract frames from video"}
            
            frame_analysis = self._analyze_video_frames(frames)
            
            system_message = (
                "You are a video editing expert. Analyze the video frames and context "
                "to provide specific editing suggestions that will enhance the final video. "
                "Focus on practical, actionable advice for video improvement."
            )
            
            prompt = f"""
VIDEO FRAMES ANALYSIS:
{frame_analysis}

TARGET MOOD: {target_mood}
SCRIPT CONTEXT: {script_context}

Provide specific suggestions for:
1. Color grading adjustments
2. Timing and pacing changes
3. Visual effects to add
4. Transition styles
5. Audio-visual synchronization improvements

Return as JSON with keys: color_grading, timing, effects, transitions, audio_sync
"""
            
            response = self._llm_client.generate_content(
                prompt=prompt,
                system_message=system_message,
                max_tokens=500,
                temperature=0.3
            )
            
            if response.content:
                try:
                    suggestions = json.loads(response.content)
self._logger.info(" Video modification suggestions generated")
                    return suggestions
                except json.JSONDecodeError:
                    return {"raw_suggestions": response.content}
            
        except Exception as e:
self._logger.error(f"Error in video modification analysis: {e}")
        
        return {"error": "Failed to generate suggestions"}
    
    def _extract_frames_from_video(self, video_path: str, num_frames: int = 3) -> List[str]:
        """
        Extrai frames de um vídeo para análise.
        
        Args:
            video_path: Path do vídeo
            num_frames: Número de frames para extrair
            
        Returns:
            Lista de paths para os frames extraídos
        """
        frames = []
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return frames
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                cap.release()
                return frames
            
            # Extrair frames distribuídos uniformemente
            frame_indices = [i * total_frames // num_frames for i in range(num_frames)]
            
            temp_dir = Path("/tmp/aishorts_frames")
            temp_dir.mkdir(exist_ok=True)
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    frame_path = temp_dir / f"frame_{frame_idx}.jpg"
                    cv2.imwrite(str(frame_path), frame)
                    frames.append(str(frame_path))
            
            cap.release()
            
        except Exception as e:
self._logger.error(f"Error extracting frames: {e}")
        
        return frames
