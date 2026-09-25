using UnityEngine;

namespace DragonFinder.Runtime.Data
{
    [CreateAssetMenu(menuName = "Dragon Finder/Dragon Definition")]
    public sealed class DragonDefinition : ScriptableObject
    {
        [SerializeField] private string id;
        [SerializeField] private string displayName;
        [SerializeField] private int stars;
        [SerializeField] private string colorHtml;
        [SerializeField] private string accessibilityLabel;

        public string Id => id;
        public string DisplayName => displayName;
        public int Stars => stars;
        public string AccessibilityLabel => accessibilityLabel;

        public Color Color
        {
            get
            {
                return ColorUtility.TryParseHtmlString(colorHtml, out Color value) ? value : Color.white;
            }
        }

        public void Initialize(string valueId, string valueDisplayName, int valueStars, string valueColorHtml, string valueAccessibilityLabel)
        {
            id = valueId;
            displayName = valueDisplayName;
            stars = valueStars;
            colorHtml = valueColorHtml;
            accessibilityLabel = valueAccessibilityLabel;
        }
    }
}
