"""
KrishakBondhu - Seed Data Script
Seeds the disease_info collection with all 38 PlantVillage disease entries
and creates a default admin user.

Usage: python seed_data.py
"""

import asyncio
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.core.security import hash_password

# All 38 PlantVillage classes with symptoms and remedies
DISEASE_DATA = [
    {
        "disease_name": "Apple___Apple_scab",
        "plant": "Apple",
        "symptoms": ["Olive-green to brown velvety spots on leaves", "Scabby lesions on fruit surface", "Premature leaf drop", "Deformed or cracked fruit"],
        "remedy": "Apply fungicides like Captan or Mancozeb during early spring. Remove and destroy fallen leaves. Prune trees for better air circulation.",
        "prevention": "Plant scab-resistant varieties. Ensure good air circulation. Apply preventive fungicide sprays before bloom.",
    },
    {
        "disease_name": "Apple___Black_rot",
        "plant": "Apple",
        "symptoms": ["Purple or reddish-brown spots on leaves", "Frogeye leaf spots with brown margins", "Black, rotting fruit with concentric rings", "Cankers on branches"],
        "remedy": "Prune and destroy infected branches and mummified fruits. Apply fungicides containing Captan or Thiophanate-methyl.",
        "prevention": "Remove dead wood and mummified fruit. Maintain tree vigor through proper fertilization. Apply dormant sprays.",
    },
    {
        "disease_name": "Apple___Cedar_apple_rust",
        "plant": "Apple",
        "symptoms": ["Bright orange-yellow spots on upper leaf surface", "Cup-shaped structures on leaf undersides", "Spots on fruit surface", "Premature leaf and fruit drop"],
        "remedy": "Apply fungicides like Myclobutanil at pink bud stage. Remove nearby juniper/cedar trees if possible.",
        "prevention": "Plant rust-resistant apple varieties. Remove cedar trees within 2-mile radius. Apply protective fungicides.",
    },
    {
        "disease_name": "Apple___healthy",
        "plant": "Apple",
        "symptoms": [],
        "remedy": "No treatment needed. Continue regular maintenance practices.",
        "prevention": "Maintain proper watering, fertilization, and pruning schedules. Monitor regularly for early signs of disease.",
    },
    {
        "disease_name": "Blueberry___healthy",
        "plant": "Blueberry",
        "symptoms": [],
        "remedy": "No treatment needed. Continue regular maintenance practices.",
        "prevention": "Maintain acidic soil pH (4.5-5.5). Ensure proper drainage and mulching. Prune annually.",
    },
    {
        "disease_name": "Cherry_(including_sour)___Powdery_mildew",
        "plant": "Cherry",
        "symptoms": ["White powdery coating on leaves", "Leaf curling and distortion", "Stunted shoot growth", "Premature leaf drop"],
        "remedy": "Apply sulfur-based or potassium bicarbonate fungicides. Remove and destroy infected plant parts.",
        "prevention": "Ensure good air circulation. Avoid overhead irrigation. Plant resistant varieties. Apply preventive fungicides.",
    },
    {
        "disease_name": "Cherry_(including_sour)___healthy",
        "plant": "Cherry",
        "symptoms": [],
        "remedy": "No treatment needed. Continue regular care.",
        "prevention": "Regular pruning, proper irrigation, and annual soil testing.",
    },
    {
        "disease_name": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
        "plant": "Corn",
        "symptoms": ["Rectangular gray to tan lesions on leaves", "Lesions run parallel to leaf veins", "Lower leaves affected first", "Severe cases cause premature death of leaves"],
        "remedy": "Apply foliar fungicides (strobilurins or triazoles). Rotate crops with non-host plants. Use resistant hybrids.",
        "prevention": "Crop rotation with soybeans or small grains. Till crop residue. Plant resistant hybrids. Avoid continuous corn planting.",
    },
    {
        "disease_name": "Corn_(maize)___Common_rust_",
        "plant": "Corn",
        "symptoms": ["Small reddish-brown pustules on both leaf surfaces", "Pustules turn dark brown to black as they mature", "Severe infection causes leaf yellowing", "Reduced grain fill"],
        "remedy": "Apply fungicides if infection is severe before tasseling. Plant resistant hybrids.",
        "prevention": "Plant resistant hybrids. Early planting to avoid peak rust periods. Monitor fields regularly.",
    },
    {
        "disease_name": "Corn_(maize)___Northern_Leaf_Blight",
        "plant": "Corn",
        "symptoms": ["Long elliptical gray-green to tan lesions on leaves", "Lesions 1-6 inches long", "Cigar-shaped lesions", "Lower leaves affected first"],
        "remedy": "Apply foliar fungicides at first sign of disease. Use resistant hybrids. Rotate crops.",
        "prevention": "Plant resistant hybrids. Rotate with non-host crops. Reduce surface residue through tillage.",
    },
    {
        "disease_name": "Corn_(maize)___healthy",
        "plant": "Corn",
        "symptoms": [],
        "remedy": "No treatment needed. Continue standard agricultural practices.",
        "prevention": "Proper spacing, adequate fertilization, and regular scouting for pests and diseases.",
    },
    {
        "disease_name": "Grape___Black_rot",
        "plant": "Grape",
        "symptoms": ["Tan circular lesions on leaves with dark borders", "Black, shriveled mummified berries", "Brown cankers on shoots", "Rapid fruit decay"],
        "remedy": "Apply fungicides (Mancozeb, Myclobutanil) from bud break through fruit development. Remove mummified berries and infected canes.",
        "prevention": "Prune for good air circulation. Remove mummified fruit. Apply preventive fungicides starting at early shoot growth.",
    },
    {
        "disease_name": "Grape___Esca_(Black_Measles)",
        "plant": "Grape",
        "symptoms": ["Tiger-striped pattern on leaves", "Dark spotting on berries", "Bleached or dried berries", "Internal wood decay"],
        "remedy": "No effective chemical cure exists. Remove and destroy severely affected vines. Apply wound protectants after pruning.",
        "prevention": "Avoid large pruning wounds. Apply wound sealant. Minimize vine stress. Remove and replace severely diseased vines.",
    },
    {
        "disease_name": "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
        "plant": "Grape",
        "symptoms": ["Small dark brown spots on leaves", "Spots enlarge and merge", "Leaf margins turn brown and dry", "Premature defoliation"],
        "remedy": "Apply Mancozeb or Copper-based fungicides. Remove and destroy infected leaves. Improve air circulation.",
        "prevention": "Proper canopy management. Regular fungicide applications. Good vineyard sanitation.",
    },
    {
        "disease_name": "Grape___healthy",
        "plant": "Grape",
        "symptoms": [],
        "remedy": "No treatment needed. Continue regular vineyard management.",
        "prevention": "Proper training and trellising. Regular monitoring. Balanced nutrition program.",
    },
    {
        "disease_name": "Orange___Haunglongbing_(Citrus_greening)",
        "plant": "Orange",
        "symptoms": ["Asymmetric yellowing of leaves (blotchy mottle)", "Small lopsided fruit", "Bitter-tasting juice", "Premature fruit drop", "Green fruit that never ripens properly"],
        "remedy": "No cure exists. Remove and destroy infected trees. Control Asian citrus psyllid vectors with insecticides.",
        "prevention": "Use disease-free nursery stock. Control psyllid populations. Regular scouting. Nutritional supplementation to maintain tree health.",
    },
    {
        "disease_name": "Peach___Bacterial_spot",
        "plant": "Peach",
        "symptoms": ["Small dark spots on leaves", "Lesions crack and fall out creating shot-hole appearance", "Dark sunken spots on fruit", "Twig cankers"],
        "remedy": "Apply copper-based bactericides. Oxytetracycline sprays during bloom. Remove severely infected branches.",
        "prevention": "Plant resistant varieties. Avoid overhead irrigation. Apply preventive copper sprays. Maintain tree vigor.",
    },
    {
        "disease_name": "Peach___healthy",
        "plant": "Peach",
        "symptoms": [],
        "remedy": "No treatment needed. Continue regular orchard management.",
        "prevention": "Annual pruning. Balanced fertilization. Regular monitoring for pests and diseases.",
    },
    {
        "disease_name": "Pepper,_bell___Bacterial_spot",
        "plant": "Pepper",
        "symptoms": ["Small water-soaked spots on leaves", "Spots turn brown with yellow halos", "Raised scab-like spots on fruit", "Severe defoliation in wet weather"],
        "remedy": "Apply copper-based bactericides. Remove and destroy infected plants. Avoid working with wet plants.",
        "prevention": "Use disease-free seed and transplants. Crop rotation (2-3 years). Avoid overhead irrigation. Plant resistant varieties.",
    },
    {
        "disease_name": "Pepper,_bell___healthy",
        "plant": "Pepper",
        "symptoms": [],
        "remedy": "No treatment needed. Continue standard care practices.",
        "prevention": "Proper spacing. Adequate water and nutrition. Regular pest scouting.",
    },
    {
        "disease_name": "Potato___Early_blight",
        "plant": "Potato",
        "symptoms": ["Dark brown concentric ring spots on lower leaves", "Target-board pattern on lesions", "Yellowing around lesions", "Premature defoliation"],
        "remedy": "Apply fungicides (Chlorothalonil, Mancozeb). Remove infected plant debris. Ensure proper plant nutrition.",
        "prevention": "Crop rotation (3 years). Use certified disease-free seed. Maintain adequate nitrogen levels. Avoid overhead irrigation.",
    },
    {
        "disease_name": "Potato___Late_blight",
        "plant": "Potato",
        "symptoms": ["Water-soaked dark green to brown lesions on leaves", "White fuzzy growth on leaf undersides in humid conditions", "Rapid plant death in wet weather", "Brown to purple tuber rot"],
        "remedy": "Apply fungicides immediately (Chlorothalonil, Metalaxyl). Destroy infected plants. Harvest tubers in dry conditions.",
        "prevention": "Plant resistant varieties. Use certified seed. Destroy volunteer plants and cull piles. Monitor weather conditions for blight forecasts.",
    },
    {
        "disease_name": "Potato___healthy",
        "plant": "Potato",
        "symptoms": [],
        "remedy": "No treatment needed. Continue standard potato management.",
        "prevention": "Proper hilling. Adequate irrigation. Crop rotation. Use certified seed potatoes.",
    },
    {
        "disease_name": "Raspberry___healthy",
        "plant": "Raspberry",
        "symptoms": [],
        "remedy": "No treatment needed. Continue regular care.",
        "prevention": "Proper trellising. Annual pruning of spent canes. Good air circulation.",
    },
    {
        "disease_name": "Soybean___healthy",
        "plant": "Soybean",
        "symptoms": [],
        "remedy": "No treatment needed. Continue standard soybean management.",
        "prevention": "Proper row spacing. Seed treatment. Regular scouting for pests and diseases.",
    },
    {
        "disease_name": "Squash___Powdery_mildew",
        "plant": "Squash",
        "symptoms": ["White powdery patches on upper leaf surfaces", "Leaves turn yellow and brown", "Premature leaf death", "Reduced fruit quality and yield"],
        "remedy": "Apply sulfur-based fungicides or potassium bicarbonate. Neem oil sprays. Remove severely infected leaves.",
        "prevention": "Plant resistant varieties. Ensure good air circulation. Avoid overhead watering. Apply preventive fungicides.",
    },
    {
        "disease_name": "Strawberry___Leaf_scorch",
        "plant": "Strawberry",
        "symptoms": ["Dark purple spots on upper leaf surface", "Spots merge causing leaf scorch appearance", "Leaf margins dry and curl upward", "Reduced plant vigor and yield"],
        "remedy": "Apply fungicides (Captan, Myclobutanil). Remove and destroy infected leaves. Renovate beds after harvest.",
        "prevention": "Use disease-free transplants. Proper plant spacing. Avoid overhead irrigation. Fungicide applications during wet weather.",
    },
    {
        "disease_name": "Strawberry___healthy",
        "plant": "Strawberry",
        "symptoms": [],
        "remedy": "No treatment needed. Continue regular strawberry care.",
        "prevention": "Proper spacing. Mulching. Regular runners management. Adequate nutrition.",
    },
    {
        "disease_name": "Tomato___Bacterial_spot",
        "plant": "Tomato",
        "symptoms": ["Small dark brown to black spots on leaves", "Spots may have yellow halos", "Raised scabby spots on fruit", "Severe defoliation"],
        "remedy": "Apply copper-based bactericides. Remove and destroy infected plants. Avoid working with wet plants.",
        "prevention": "Use disease-free seed. Crop rotation. Avoid overhead irrigation. Disinfect tools between plants.",
    },
    {
        "disease_name": "Tomato___Early_blight",
        "plant": "Tomato",
        "symptoms": ["Dark concentric ring spots on lower leaves", "Target-board pattern lesions", "Stem lesions near soil line", "Fruit rot at stem end"],
        "remedy": "Apply Chlorothalonil or Mancozeb fungicides. Remove lower infected leaves. Stake plants for air circulation.",
        "prevention": "Crop rotation. Mulching to prevent soil splash. Remove plant debris. Use resistant varieties.",
    },
    {
        "disease_name": "Tomato___Late_blight",
        "plant": "Tomato",
        "symptoms": ["Large water-soaked gray-green spots on leaves", "White fuzzy growth on leaf undersides", "Rapid plant collapse in wet weather", "Brown firm fruit rot"],
        "remedy": "Apply fungicides immediately (Chlorothalonil, Copper). Remove and destroy all infected plant material. Do not compost.",
        "prevention": "Plant resistant varieties. Ensure good air circulation. Avoid overhead watering. Monitor weather for blight conditions.",
    },
    {
        "disease_name": "Tomato___Leaf_Mold",
        "plant": "Tomato",
        "symptoms": ["Pale yellow spots on upper leaf surface", "Olive-green to brown velvety mold on leaf undersides", "Leaves curl and wither", "Mainly occurs in greenhouse conditions"],
        "remedy": "Improve ventilation and reduce humidity. Apply fungicides (Chlorothalonil). Remove infected leaves.",
        "prevention": "Ensure good air circulation in greenhouses. Reduce humidity. Use resistant varieties. Avoid leaf wetness.",
    },
    {
        "disease_name": "Tomato___Septoria_leaf_spot",
        "plant": "Tomato",
        "symptoms": ["Small circular spots with dark brown borders and gray centers", "Tiny dark specks (pycnidia) visible in spot centers", "Lower leaves affected first", "Severe defoliation"],
        "remedy": "Apply Chlorothalonil or Copper-based fungicides. Remove and destroy lower infected leaves. Mulch around plants.",
        "prevention": "Crop rotation (3 years). Remove plant debris. Mulch to prevent soil splash. Avoid overhead irrigation.",
    },
    {
        "disease_name": "Tomato___Spider_mites Two-spotted_spider_mite",
        "plant": "Tomato",
        "symptoms": ["Fine stippling/speckling on leaves", "Tiny webs on leaf undersides", "Leaves turn bronze or yellow", "Severely infested leaves dry up and fall"],
        "remedy": "Spray with miticides or insecticidal soap. Neem oil applications. Introduce predatory mites (Phytoseiulus persimilis).",
        "prevention": "Monitor plants regularly. Maintain adequate humidity. Avoid dusty conditions. Introduce beneficial insects early.",
    },
    {
        "disease_name": "Tomato___Target_Spot",
        "plant": "Tomato",
        "symptoms": ["Brown spots with concentric rings on leaves", "Spots may have yellow halos", "Lesions on stems and fruit", "Lower leaves affected first"],
        "remedy": "Apply Chlorothalonil or Mancozeb fungicides. Remove infected plant parts. Improve air circulation.",
        "prevention": "Crop rotation. Proper plant spacing. Avoid overhead irrigation. Remove plant debris.",
    },
    {
        "disease_name": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
        "plant": "Tomato",
        "symptoms": ["Severe upward leaf curling", "Yellowing of leaf margins", "Stunted plant growth", "Flower drop and reduced fruit set"],
        "remedy": "No cure for virus. Remove and destroy infected plants. Control whitefly vectors with insecticides or sticky traps.",
        "prevention": "Use resistant varieties. Control whitefly populations. Use reflective mulches. Install insect screens in greenhouses.",
    },
    {
        "disease_name": "Tomato___Tomato_mosaic_virus",
        "plant": "Tomato",
        "symptoms": ["Mosaic pattern of light and dark green on leaves", "Leaf curling and distortion", "Stunted growth", "Mottled or streaked fruit"],
        "remedy": "No cure for virus. Remove and destroy infected plants. Disinfect hands and tools with milk or 10% bleach solution.",
        "prevention": "Use virus-free seed and transplants. Disinfect tools. Avoid tobacco products near plants. Plant resistant varieties.",
    },
    {
        "disease_name": "Tomato___healthy",
        "plant": "Tomato",
        "symptoms": [],
        "remedy": "No treatment needed. Continue regular tomato care.",
        "prevention": "Proper staking. Adequate water and nutrition. Regular pruning of suckers. Mulching.",
    },
]


async def seed_database():
    """Seed the database with disease info and a default admin user."""
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]

    now = datetime.now(timezone.utc)

    # --- Seed disease_info ---
    print("🌱 Seeding disease_info collection...")
    seeded_count = 0
    for disease in DISEASE_DATA:
        existing = await db.disease_info.find_one({"disease_name": disease["disease_name"]})
        if not existing:
            disease["image_url"] = None
            disease["created_at"] = now
            await db.disease_info.insert_one(disease)
            seeded_count += 1

    print(f"   ✅ Seeded {seeded_count} new disease entries ({len(DISEASE_DATA)} total)")

    # --- Create default admin user ---
    print("👤 Creating default admin user...")
    admin_email = "admin@krishakbondhu.com"
    existing_admin = await db.users.find_one({"email": admin_email})

    if not existing_admin:
        admin_doc = {
            "name": "Admin",
            "email": admin_email,
            "hashed_password": hash_password("admin123"),
            "role": "admin",
            "avatar_url": None,
            "phone": None,
            "location": None,
            "created_at": now,
            "updated_at": now,
        }
        await db.users.insert_one(admin_doc)
        print(f"   ✅ Admin created: {admin_email} / admin123")
    else:
        print(f"   ⏭️  Admin already exists: {admin_email}")

    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.disease_info.create_index("disease_name", unique=True)

    client.close()
    print("\n🎉 Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_database())
