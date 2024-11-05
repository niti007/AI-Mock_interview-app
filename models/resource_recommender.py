from typing import Dict, List, Union
import json
from pathlib import Path


class ResourceRecommender:
    def __init__(self):
        # Load resource database
        self.resources = self._load_resources()

    def _load_resources(self) -> Dict[str, List[Dict[str, str]]]:
        """Load resource database from JSON file"""
        # Define default resources if file doesn't exist
        default_resources = {
            "python": [
                {
                    "title": "Python Documentation",
                    "url": "https://docs.python.org/3/",
                    "type": "documentation",
                    "level": "all"
                },
                {
                    "title": "Real Python Tutorials",
                    "url": "https://realpython.com",
                    "type": "tutorial",
                    "level": "intermediate"
                }
            ],
            "java": [
                {
                    "title": "Java Documentation",
                    "url": "https://docs.oracle.com/en/java/",
                    "type": "documentation",
                    "level": "all"
                }
            ],
            "javascript": [
                {
                    "title": "MDN Web Docs",
                    "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
                    "type": "documentation",
                    "level": "all"
                }
            ],
            "sql": [
                {
                    "title": "W3Schools SQL Tutorial",
                    "url": "https://www.w3schools.com/sql/",
                    "type": "tutorial",
                    "level": "beginner"
                }
            ],
            "behavioral": [
                {
                    "title": "STAR Method Guide",
                    "url": "https://www.indeed.com/career-advice/interviewing/how-to-use-the-star-interview-response-technique",
                    "type": "methodology",
                    "level": "all"
                }
            ],
            "system_design": [
                {
                    "title": "System Design Primer",
                    "url": "https://github.com/donnemartin/system-design-primer",
                    "type": "guide",
                    "level": "advanced"
                }
            ]
        }

        try:
            resources_path = Path("resources.json")
            if resources_path.exists():
                with open(resources_path, 'r') as f:
                    return json.load(f)
            else:
                # Create default resources file
                with open(resources_path, 'w') as f:
                    json.dump(default_resources, f, indent=4)
                return default_resources
        except Exception as e:
            print(f"Error loading resources: {str(e)}")
            return default_resources

    def get_recommendations(self,
                            cv_data: Dict,
                            interview_type: str,
                            interview_feedback: Dict,
                            technical_stack: List[str] = None) -> Dict[str, List[Dict[str, str]]]:
        """
        Generate personalized resource recommendations based on CV and interview performance

        Args:
            cv_data: Parsed CV data
            interview_type: Type of interview (technical/behavioral)
            interview_feedback: Performance feedback from interview
            technical_stack: List of technical skills (for technical interviews)

        Returns:
            Dict containing recommended resources by category
        """
        recommendations = {
            "priority": [],  # High-priority resources based on weak areas
            "skill_development": [],  # Resources for skill improvement
            "interview_prep": [],  # Interview preparation resources
            "additional": []  # Additional relevant resources
        }

        # Analyze interview feedback to identify weak areas
        weak_areas = self._identify_weak_areas(interview_feedback)

        # Get recommendations based on interview type
        if interview_type.lower() == "technical":
            self._add_technical_recommendations(
                recommendations,
                technical_stack,
                weak_areas,
                cv_data.get('skills', [])
            )
        else:
            self._add_behavioral_recommendations(
                recommendations,
                weak_areas
            )

        # Add general interview preparation resources
        self._add_general_recommendations(recommendations)

        return recommendations

    def _identify_weak_areas(self, feedback: Dict) -> List[str]:
        """Identify areas needing improvement based on interview feedback"""
        weak_areas = []

        # Check various performance metrics
        for question, metrics in feedback.items():
            if isinstance(metrics, dict):
                # Check clarity score
                if metrics.get('clarity', 1.0) < 0.7:
                    weak_areas.append('communication')

                # Check technical accuracy (for technical questions)
                if metrics.get('technical_accuracy', 1.0) < 0.7:
                    weak_areas.append('technical_knowledge')

                # Check response structure
                if metrics.get('structure', 1.0) < 0.7:
                    weak_areas.append('response_structure')

                # Check problem-solving approach
                if metrics.get('problem_solving', 1.0) < 0.7:
                    weak_areas.append('problem_solving')

        return list(set(weak_areas))  # Remove duplicates

    def _add_technical_recommendations(self,
                                       recommendations: Dict[str, List],
                                       technical_stack: List[str],
                                       weak_areas: List[str],
                                       current_skills: List[str]) -> None:
        """Add technical learning resources based on stack and weak areas"""

        # Add resources for each technology in the stack
        for tech in technical_stack:
            tech_lower = tech.lower()
            if tech_lower in self.resources:
                for resource in self.resources[tech_lower]:
                    # Prioritize resources based on weak areas
                    if 'technical_knowledge' in weak_areas:
                        recommendations['priority'].append(resource)
                    else:
                        recommendations['skill_development'].append(resource)

        # Add system design resources for experienced candidates
        if self._should_recommend_system_design(current_skills):
            recommendations['additional'].extend(self.resources.get('system_design', []))

    def _add_behavioral_recommendations(self,
                                        recommendations: Dict[str, List],
                                        weak_areas: List[str]) -> None:
        """Add behavioral interview resources based on weak areas"""

        behavioral_resources = self.resources.get('behavioral', [])

        for resource in behavioral_resources:
            if 'communication' in weak_areas or 'response_structure' in weak_areas:
                recommendations['priority'].append(resource)
            else:
                recommendations['interview_prep'].append(resource)

    def _add_general_recommendations(self, recommendations: Dict[str, List]) -> None:
        """Add general interview preparation resources"""
        general_resources = [
            {
                "title": "Mock Interview Platform",
                "url": "https://www.pramp.com",
                "type": "practice",
                "level": "all"
            },
            {
                "title": "Interview Question Bank",
                "url": "https://www.glassdoor.com/Interview/index.htm",
                "type": "preparation",
                "level": "all"
            }
        ]

        recommendations['interview_prep'].extend(general_resources)

    def _should_recommend_system_design(self, skills: List[str]) -> bool:
        """Determine if system design resources should be recommended"""
        senior_indicators = ['architecture', 'system design', 'distributed systems',
                             'scalability', 'microservices', 'aws', 'azure', 'gcp']

        return any(indicator in skill.lower() for skill in skills
                   for indicator in senior_indicators)