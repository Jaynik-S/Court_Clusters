from nba_api.stats.static import players
from collections import defaultdict
import career_stats as cs
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

nba_players = [
"LeBron James","Kevin Durant","Stephen Curry","Giannis Antetokounmpo","Nikola Jokić","Joel Embiid","Luka Dončić","James Harden","Damian Lillard","Jayson Tatum","Devin Booker","Kawhi Leonard"]#,"Paul George","Kyrie Irving","Jimmy Butler","Anthony Davis","Chris Paul","Trae Young","Donovan Mitchell","Bradley Beal","Zion Williamson","Ja Morant","Russell Westbrook","Karl-Anthony Towns","Draymond Green","Bam Adebayo","Rudy Gobert","Ben Simmons","Klay Thompson","Andrew Wiggins","Pascal Siakam","DeMar DeRozan","Zach LaVine","Brandon Ingram","Jaylen Brown","LaMelo Ball","Anthony Edwards","Domantas Sabonis","De'Aaron Fox","CJ McCollum","Khris Middleton","Jrue Holiday","Mikal Bridges","Jerami Grant","Steven Adams","Clint Capela","Myles Turner","Fred VanVleet","Kyle Lowry","Gordon Hayward","Kristaps Porziņģis","Julius Randle","Shai Gilgeous-Alexander","Darius Garland","Evan Mobley","Cade Cunningham","Tyrese Haliburton","Tyler Herro","RJ Barrett","Miles Bridges","Terry Rozier","Derrick Rose","Victor Oladipo","Malcolm Brogdon","Al Horford","Brook Lopez","Mitchell Robinson","Buddy Hield","Gary Trent Jr.","Michael Porter Jr.","Christian Wood","Spencer Dinwiddie","Caris LeVert","Montrezl Harrell","T.J. Warren","Eric Gordon","Derrick White","John Collins","Nikola Vučević","Aaron Gordon","Bojan Bogdanović","Marcus Smart","Lauri Markkanen","Robert Covington","Norman Powell","Serge Ibaka","Jarrett Allen","Seth Curry","Joe Ingles","Tim Hardaway Jr.","Reggie Jackson","Harrison Barnes","Mo Bamba","Jaren Jackson Jr.","Bogdan Bogdanović","Rui Hachimura","Kyle Kuzma","Jordan Clarkson","Richaun Holmes","D'Angelo Russell","Quentin Grimes","Dejounte Murray","Keldon Johnson","Lonzo Ball","Coby White","Alex Caruso","Jericho Sims","Devin Vassell","James Wiseman","Deandre Ayton","Franz Wagner","Jordan Poole","Kevin Porter Jr.","Patrick Beverley","Doug McDermott","Davis Bertans","Kelly Olynyk","Daniel Gafford","Cam Reddish","Trey Murphy III"]
print(nba_players)


players_id = []
for player in nba_players:
    clean_player_name = player.split(' (')[0].strip()
    player_dict = players.find_players_by_full_name(clean_player_name)
    if player_dict:
        # If player found, get their ID
        player_id = player_dict[0]['id']
        players_id.append(player_id)
    else:
        print(f"Player not found: {player}")



players_data = []

for p_id in players_id:
    one, two, three = cs.get_player_career_stats(p_id)
    full_stats = cs.merged_df(one, two, three)
    numeric_stats = full_stats.select_dtypes(include=[np.number])
    
    # Flatten the numeric stats into a single row
    print('check')
    
    players_data.append(numeric_stats.values.flatten())

players_array = np.array(players_data)
players_array = np.nan_to_num(players_array)

# Scale the data
scaler = StandardScaler()
scaled_data = scaler.fit_transform(players_array)

# Apply KMeans
kmeans = KMeans(n_clusters=5, random_state=42, n_init=20)
kmeans.fit(scaled_data)

# Retrieve cluster labels and centroids
labels = kmeans.labels_
centroids = kmeans.cluster_centers_

print("Cluster Labels:", labels)

# Reduce dimensionality to 2D for plotting
pca = PCA(n_components=2)
reduced_data = pca.fit_transform(scaled_data)
reduced_centroids = pca.transform(centroids)

# Plot the clusters
plt.figure(figsize=(10, 7))
for cluster_id in np.unique(labels):
    cluster_points = reduced_data[labels == cluster_id]
    plt.scatter(
        cluster_points[:, 0],
        cluster_points[:, 1],
        label=f"Cluster {cluster_id}",
        alpha=0.7,
    )

# Plot the centroids
plt.scatter(
    reduced_centroids[:, 0],
    reduced_centroids[:, 1],
    c="red",
    marker="x",
    s=200,
    label="Centroids",
)

# Annotate each point with the player's first name
for i, player_name in enumerate(nba_players):
    first_name = player_name.split()[0]  # Extract the first name
    plt.text(
        reduced_data[i, 0],
        reduced_data[i, 1],
        first_name,
        fontsize=10,
        ha="right",  # Align the text to the right of the point
        color="black",
    )
    
# Create a dictionary to store the output
cluster_dict = {}

# Iterate through each unique cluster label
for cluster_id in np.unique(labels):
    # Get the names of players in the current cluster
    players_in_cluster = [nba_players[i] for i in range(len(labels)) if labels[i] == cluster_id]
    
    # Get the coordinates of the current centroid
    centroid_coords = reduced_centroids[cluster_id].tolist()
    
    # Format the dictionary
    cluster_dict[f"Cluster_{cluster_id}"] = [players_in_cluster, centroid_coords]

# Print the resulting dictionary
print(cluster_dict)


# Add labels and legend
plt.title("NBA Player Archetype Clusters")
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.legend()
plt.show()

