from typing import Annotated

from sqlmodel import Field, Session, SQLModel, create_engine, select

from db.models import Video, Clip

sqlite_filename = "database.db"
sqlite_url = f"sqlite:///{sqlite_filename}"


supabase_name = "NA.db"
supabase_url = f"supabase:///{supabase_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# def create_heroes():
#     vid_1 = Video(name="Deadpond", video="boo", transcript="blah")
#     vid_2 = Video(name="Spider-Boy",  video="boo", transcript="blah")
#     vid_3 = Video(name="Rusty-Man", video="boo", transcript="blah")

#     clip1 = Clip(name="Dead1", start="00.00", end="01.00", link="boo")
#     clip2 = Clip(name="Dead1", start="01.00", end="02.00", link="boo")
#     clip3 = Clip(name="Dead1", start="02.00", end="03.00", link="boo")

#     with Session(engine) as session:
#         session.add(vid_1)
#         session.add(vid_2)
#         session.add(vid_3)

#         session.commit()
#         print("After committing the session")
#         print("Vid 1:", vid_1)
#         print("Vid 2:", vid_2)
#         print("Vid 3:", vid_3)

#         session.refresh(vid_1)
#         session.refresh(vid_2)
#         session.refresh(vid_3)

#         print("After refreshing the heroes")
#         print("Vid 1:", vid_1)
#         print("Vid 2:", vid_2)
#         print("Vid 3:", vid_3)
        
#         vid_1.clips.append(clip1)
#         vid_1.clips.append(clip2)
#         vid_1.clips.append(clip3)

#         session.add(vid_1)
#         session.commit()
#         session.refresh(clip1)
#         session.refresh(clip2)
#         session.refresh(clip3)
#         print("Vid1 Clips")
#         print("Clip 1:", clip1)
#         print("Clip 2:", clip2)
#         print("Clip 3:", clip3)

#     print("YAHHOOO")


# def select_heroes():
#     with Session(engine) as session:
#         statement = select(Video).where(Video.name == "Deadpond")
#         results = session.exec(statement)
#         for hero in results:
#             print(hero)

# def main():
#     create_db_and_tables()
#     create_heroes()
#     select_heroes()

# if __name__ == "__main__":
#     main()



