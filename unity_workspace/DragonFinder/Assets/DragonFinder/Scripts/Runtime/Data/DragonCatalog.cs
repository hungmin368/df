using System;
using System.Collections.Generic;
using UnityEngine;

namespace DragonFinder.Runtime.Data
{
    [CreateAssetMenu(menuName = "Dragon Finder/Dragon Catalog")]
    public sealed class DragonCatalog : ScriptableObject
    {
        [SerializeField] private List<DragonDefinition> dragons = new List<DragonDefinition>();

        public IReadOnlyList<DragonDefinition> Dragons => dragons;

        public void Initialize(IEnumerable<DragonDefinition> values)
        {
            dragons = new List<DragonDefinition>(values ?? throw new ArgumentNullException(nameof(values)));
        }

        public DragonDefinition Find(string id)
        {
            return dragons.Find(dragon => dragon != null && dragon.Id == id);
        }
    }
}
