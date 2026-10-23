"""Stable photo names and landmark-local camera poses for the heist planner."""
ROOMS=[
 ('01_ground/01_queens_hall','VIC_ROOM_MAIN_HALL','queens_hall',(0,13,25),(0,20,-10)),
 ('01_ground/02_public_gallery','VIC_ROOM_PUBLIC','public_gallery',(-62,13,-87),(-39,14,-67)),
 ('01_ground/03_collections','VIC_ROOM_GALLERY_C','collections_gallery',(-85,13,-66),(-71,14,-86)),
 ('01_ground/04_painting_gallery','VIC_ROOM_GALLERY_A','painting_gallery',(-84,13,70),(-48,14,80)),
 ('01_ground/05_sculpture_gallery','VIC_ROOM_GALLERY_B','sculpture_gallery',(84,13,82),(48,14,70)),
 ('01_ground/06_high_security','VIC_ROOM_HIGH_SECURITY','high_security',(66,13,-64),(43,14,-86)),
 ('01_ground/07_archive','VIC_ROOM_ARCHIVE','archive',(86,13,-65),(74,13,-82)),
 ('02_upper/01_overlook','VIC_ROOM_UPPER_HALL','upper_balcony',(0,40,25),(0,42,-26)),
 ('02_upper/02_north_landing','VIC_ROOM_UPPER_NORTH','upper_stair_landing',(-15,40,-84),(8,39,-49)),
 ('02_upper/03_south_landing','VIC_ROOM_UPPER_SOUTH',None,(12,40,44),(-10,38,70)),
 ('02_upper/04_screening','VIC_ROOM_UPPER_SCREENING','upper_screening',(-25,40,-86),(-18,40,-58)),
 ('02_upper/05_treasury','VIC_ROOM_UPPER_TREASURY','upper_treasury',(-84,40,-68),(-48,40,-79)),
 ('02_upper/06_royal_collection','VIC_ROOM_UPPER_ROYAL','upper_royal',(84,40,-68),(48,40,-79)),
 ('02_upper/07_river_gallery','VIC_ROOM_UPPER_RIVER','upper_river',(-84,40,84),(-48,40,72)),
 ('02_upper/08_craft_gallery','VIC_ROOM_UPPER_CRAFT','upper_craft',(84,40,84),(48,40,72)),
]
EXTRA=[
 ('03_circulation/north_stair','north_stair',None,None),
 ('03_circulation/south_stair','south_stair',None,None),
 ('04_routes/main_portal',None,(0,12,-100),(0,15,-60)),
 ('04_routes/rear_portal',None,(0,12,100),(0,15,60)),
 ('04_routes/side_a',None,(-110,12,0),(-22,14,0)),
 ('04_routes/side_b',None,(110,12,0),(22,14,0)),
]
if __name__=='__main__':
 import json
 jobs=[dict(file=folder+'/02_reverse.png' if forward else folder+'/01_approach.png',roomId=id,localEye=eye,localTarget=target) for folder,id,forward,eye,target in ROOMS]
 jobs += [dict(file=folder+'/01_route.png',localEye=eye,localTarget=target) for folder,forward,eye,target in EXTRA if eye]
 print(json.dumps(jobs))
