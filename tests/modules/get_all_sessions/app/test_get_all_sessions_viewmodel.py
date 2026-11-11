from src.modules.get_all_sessions.app.get_all_sessions_viewmodel import GetAllSessionsViewmodel, SessionViewmodel
from src.shared.domain.entities.session import Session


class Test_GetAllSessionsViewmodel:
    all_sessions_list = [
        Session(
            session_id="1753651605588001kjXl",
            short_id="TNC301",
            title="Accelerate VMware Migration with AWS Transform",
            abstract="This bootcamp is for AWS Partners only.",
            session_type="Bootcamp",
            venue_name="Mandalay Bay",
            venue_room="Level 2 South | Breakers K",
            start_datetime="2025-12-04T21:00:00.000Z",
            end_datetime="2025-12-05T01:00:00.000Z",
            day="Thursday",
            speakers=[{"displayName": "Parvesh Chopra", "company": "AWS"}],
            topics=["Artificial Intelligence"],
            areas_of_interest=["Training & Certification"],
            level="300 – Advanced",
            level_value=300,
            features=["Hands-on"],
            seat_capacity=126
        ),
        Session(
            session_id="1753651605588002abCD",
            short_id="SVS201",
            title="Building Serverless Applications",
            abstract="Learn serverless fundamentals.",
            session_type="Breakout Session",
            venue_name="Venetian",
            venue_room="Level 3 | Marcello 4405",
            start_datetime="2025-12-05T14:00:00.000Z",
            end_datetime="2025-12-05T15:00:00.000Z",
            day="Friday",
            speakers=[
                {"displayName": "Jane Smith", "company": "AWS"},
                {"displayName": "John Doe", "company": "AWS"}
            ],
            topics=["Serverless", "Compute"],
            areas_of_interest=["Application Development"],
            level="200 – Intermediate",
            level_value=200,
            features=["Interactive"],
            seat_capacity=250
        )
    ]

    def test_get_all_sessions_viewmodel(self):
        viewmodel = GetAllSessionsViewmodel(self.all_sessions_list)

        expected = {
            "sessions": [
                {
                    'session_id': "1753651605588001kjXl",
                    'short_id': "TNC301",
                    'title': "Accelerate VMware Migration with AWS Transform",
                    'abstract': "This bootcamp is for AWS Partners only.",
                    'session_type': "Bootcamp",
                    'venue_name': "Mandalay Bay",
                    'venue_room': "Level 2 South | Breakers K",
                    'start_datetime': "2025-12-04T21:00:00.000Z",
                    'end_datetime': "2025-12-05T01:00:00.000Z",
                    'day': "Thursday",
                    'speakers': [{"displayName": "Parvesh Chopra", "company": "AWS"}],
                    'topics': ["Artificial Intelligence"],
                    'areas_of_interest': ["Training & Certification"],
                    'level': "300 – Advanced",
                    'level_value': 300,
                    'features': ["Hands-on"],
                    'seat_capacity': 126
                },
                {
                    'session_id': "1753651605588002abCD",
                    'short_id': "SVS201",
                    'title': "Building Serverless Applications",
                    'abstract': "Learn serverless fundamentals.",
                    'session_type': "Breakout Session",
                    'venue_name': "Venetian",
                    'venue_room': "Level 3 | Marcello 4405",
                    'start_datetime': "2025-12-05T14:00:00.000Z",
                    'end_datetime': "2025-12-05T15:00:00.000Z",
                    'day': "Friday",
                    'speakers': [
                        {"displayName": "Jane Smith", "company": "AWS"},
                        {"displayName": "John Doe", "company": "AWS"}
                    ],
                    'topics': ["Serverless", "Compute"],
                    'areas_of_interest': ["Application Development"],
                    'level': "200 – Intermediate",
                    'level_value': 200,
                    'features': ["Interactive"],
                    'seat_capacity': 250
                }
            ],
            "count": 2
        }

        response = viewmodel.to_dict()

        assert response == expected

    def test_get_all_sessions_viewmodel_empty_list(self):
        viewmodel = GetAllSessionsViewmodel([])

        expected = {
            "sessions": [],
            "count": 0
        }

        response = viewmodel.to_dict()

        assert response == expected

    def test_session_viewmodel(self):
        session = Session(
            session_id="1753651605588001kjXl",
            short_id="TNC301",
            title="Accelerate VMware Migration with AWS Transform",
            abstract="This bootcamp is for AWS Partners only.",
            session_type="Bootcamp",
            venue_name="Mandalay Bay",
            venue_room="Level 2 South | Breakers K",
            start_datetime="2025-12-04T21:00:00.000Z",
            end_datetime="2025-12-05T01:00:00.000Z",
            day="Thursday",
            speakers=[{"displayName": "Parvesh Chopra", "company": "AWS"}],
            topics=["Artificial Intelligence"],
            areas_of_interest=["Training & Certification"],
            level="300 – Advanced",
            level_value=300,
            features=["Hands-on"],
            seat_capacity=126
        )

        viewmodel = SessionViewmodel(session)
        response = viewmodel.to_dict()

        expected = {
            'session_id': "1753651605588001kjXl",
            'short_id': "TNC301",
            'title': "Accelerate VMware Migration with AWS Transform",
            'abstract': "This bootcamp is for AWS Partners only.",
            'session_type': "Bootcamp",
            'venue_name': "Mandalay Bay",
            'venue_room': "Level 2 South | Breakers K",
            'start_datetime': "2025-12-04T21:00:00.000Z",
            'end_datetime': "2025-12-05T01:00:00.000Z",
            'day': "Thursday",
            'speakers': [{"displayName": "Parvesh Chopra", "company": "AWS"}],
            'topics': ["Artificial Intelligence"],
            'areas_of_interest': ["Training & Certification"],
            'level': "300 – Advanced",
            'level_value': 300,
            'features': ["Hands-on"],
            'seat_capacity': 126
        }

        assert response == expected
