
import React, { useState } from 'react';
import { Info } from 'lucide-react';

const CorruptionDefinitions = () => {
  const [hoveredArea, setHoveredArea] = useState(null);

  const definitions = {
    legal: {
      title: "Legal Definition",
      color: "#3b82f6",
      description: "Focuses on the ACT - breach of law",
      examples: [
        "Bribery: A government official accepting money to approve a construction permit",
        "Embezzlement: A public servant siphoning funds from a development project",
        "Fraud: Falsifying documents to win a government contract"
      ]
    },
    moral: {
      title: "Moral/Ethical Definition",
      color: "#ef4444",
      description: "Focuses on the INTENT - self-interest vs public good",
      examples: [
        "A politician prioritizing party donors over constituents' needs",
        "Breaking the sanctity of social, kinship, or economic relations",
        "Violating accepted norms and religious codes of conduct"
      ]
    },
    institutional: {
      title: "Institutional Definition",
      color: "#10b981",
      description: "Focuses on WHERE it happens - context matters",
      examples: [
        "Electoral finance (normalized in politics but questioned in bureaucracy)",
        "Corporate lobbying (legal in some contexts, corrupt in others)",
        "Nepotism in hiring (varies by institution and culture)"
      ]
    },
    social: {
      title: "Social/Power Definition",
      color: "#f59e0b",
      description: "Focuses on WHO does it - power dynamics",
      examples: [
        "A poor person stealing food vs. a politician embezzling millions",
        "Caste/class affecting judgment of the same act",
        "Elite tax evasion vs. welfare fraud by the poor"
      ]
    }
  };

  const intersections = {
    legalMoral: {
      title: "Legal + Moral",
      examples: ["A judge accepting bribes (breaks law AND violates trust)"]
    },
    legalInstitutional: {
      title: "Legal + Institutional",
      examples: ["Campaign finance violations (law + political context)"]
    },
    legalSocial: {
      title: "Legal + Social",
      examples: ["Selective prosecution based on caste/class"]
    },
    moralInstitutional: {
      title: "Moral + Institutional",
      examples: ["Normalized practices like 'speed money' in bureaucracy"]
    },
    moralSocial: {
      title: "Moral + Social",
      examples: ["Nepotism judged differently for powerful vs. marginalized"]
    },
    institutionalSocial: {
      title: "Institutional + Social",
      examples: ["Corporate boards dominated by privileged networks"]
    },
    center: {
      title: "All Definitions",
      examples: ["A powerful official embezzling public funds intended for marginalized communities"]
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6 bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">Understanding Corruption: Multiple Definitions</h1>
        
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
          <p className="text-sm text-gray-700 italic">
            "Corruption is not an exception but the system's internal contradiction; it is one of the motors which run our political economy, sustain our social structures, and scaffold our personal and professional relationships."
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          {Object.entries(definitions).map(([key, def]) => (
            <div key={key} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center mb-2">
                <div className="w-4 h-4 rounded-full mr-2" style={{ backgroundColor: def.color }}></div>
                <h3 className="font-bold text-lg">{def.title}</h3>
              </div>
              <p className="text-sm text-gray-600 mb-3 font-medium">{def.description}</p>
              <div className="text-sm">
                <p className="font-semibold mb-1">Examples:</p>
                <ul className="space-y-1">
                  {def.examples.map((ex, i) => (
                    <li key={i} className="text-gray-700">• {ex}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>

        <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 mb-6">
          <div className="flex items-start">
            <Info className="w-5 h-5 text-yellow-600 mr-2 mt-0.5" />
            <div>
              <p className="font-semibold text-gray-800 mb-1">Key Insight:</p>
              <p className="text-sm text-gray-700">
                These definitions often overlap. A single corrupt act can be analyzed through multiple lenses - legal, moral, institutional, and social - revealing different dimensions of the same phenomenon.
              </p>
            </div>
          </div>
        </div>

        <h2 className="text-2xl font-bold text-gray-800 mb-4">Interactive Venn Diagram</h2>
        <p className="text-sm text-gray-600 mb-4">Hover over different areas to see examples of overlapping definitions</p>
        
        <div className="relative w-full h-96 bg-white rounded-lg border-2 border-gray-200 mb-6">
          <svg viewBox="0 0 400 300" className="w-full h-full">
            {/* Legal Circle */}
            <circle
              cx="150" cy="120" r="80"
              fill={definitions.legal.color}
              opacity="0.3"
              stroke={definitions.legal.color}
              strokeWidth="2"
              onMouseEnter={() => setHoveredArea('legal')}
              onMouseLeave={() => setHoveredArea(null)}
              className="cursor-pointer hover:opacity-40 transition-opacity"
            />
            <text x="150" y="60" textAnchor="middle" className="text-xs font-bold" fill={definitions.legal.color}>
              Legal
            </text>

            {/* Moral Circle */}
            <circle
              cx="250" cy="120" r="80"
              fill={definitions.moral.color}
              opacity="0.3"
              stroke={definitions.moral.color}
              strokeWidth="2"
              onMouseEnter={() => setHoveredArea('moral')}
              onMouseLeave={() => setHoveredArea(null)}
              className="cursor-pointer hover:opacity-40 transition-opacity"
            />
            <text x="250" y="60" textAnchor="middle" className="text-xs font-bold" fill={definitions.moral.color}>
              Moral/Ethical
            </text>

            {/* Institutional Circle */}
            <circle
              cx="150" cy="200" r="80"
              fill={definitions.institutional.color}
              opacity="0.3"
              stroke={definitions.institutional.color}
              strokeWidth="2"
              onMouseEnter={() => setHoveredArea('institutional')}
              onMouseLeave={() => setHoveredArea(null)}
              className="cursor-pointer hover:opacity-40 transition-opacity"
            />
            <text x="150" y="270" textAnchor="middle" className="text-xs font-bold" fill={definitions.institutional.color}>
              Institutional
            </text>

            {/* Social Circle */}
            <circle
              cx="250" cy="200" r="80"
              fill={definitions.social.color}
              opacity="0.3"
              stroke={definitions.social.color}
              strokeWidth="2"
              onMouseEnter={() => setHoveredArea('social')}
              onMouseLeave={() => setHoveredArea(null)}
              className="cursor-pointer hover:opacity-40 transition-opacity"
            />
            <text x="250" y="270" textAnchor="middle" className="text-xs font-bold" fill={definitions.social.color}>
              Social/Power
            </text>

            {/* Intersection markers */}
            <circle cx="200" cy="100" r="8" fill="#6366f1" opacity="0.6"
              onMouseEnter={() => setHoveredArea('legalMoral')}
              onMouseLeave={() => setHoveredArea(null)}
              className="cursor-pointer" />
            
            <circle cx="150" cy="160" r="8" fill="#6366f1" opacity="0.6"
              onMouseEnter={() => setHoveredArea('legalInstitutional')}
              onMouseLeave={() => setHoveredArea(null)}
              className="cursor-pointer" />
            
            <circle cx="250" cy="160" r="8" fill="#6366f1" opacity="0.6"
              onMouseEnter={() => setHoveredArea('moralSocial')}
              onMouseLeave={() => setHoveredArea(null)}
              className="cursor-pointer" />
            
            <circle cx="200" cy="220" r="8" fill="#6366f1" opacity="0.6"
              onMouseEnter={() => setHoveredArea('institutionalSocial')}
              onMouseLeave={() => setHoveredArea(null)}
              className="cursor-pointer" />

            <circle cx="200" cy="160" r="10" fill="#8b5cf6" opacity="0.8"
              onMouseEnter={() => setHoveredArea('center')}
              onMouseLeave={() => setHoveredArea(null)}
              className="cursor-pointer" />
          </svg>
        </div>

        {hoveredArea && (
          <div className="bg-purple-50 border-2 border-purple-300 rounded-lg p-4 mb-6 animate-fadeIn">
            <h3 className="font-bold text-lg text-purple-900 mb-2">
              {hoveredArea === 'legal' && definitions.legal.title}
              {hoveredArea === 'moral' && definitions.moral.title}
              {hoveredArea === 'institutional' && definitions.institutional.title}
              {hoveredArea === 'social' && definitions.social.title}
              {hoveredArea !== 'legal' && hoveredArea !== 'moral' && hoveredArea !== 'institutional' && hoveredArea !== 'social' && intersections[hoveredArea]?.title}
            </h3>
            <p className="text-sm text-gray-700">
              <span className="font-semibold">Example: </span>
              {hoveredArea === 'legal' && definitions.legal.examples[0]}
              {hoveredArea === 'moral' && definitions.moral.examples[0]}
              {hoveredArea === 'institutional' && definitions.institutional.examples[0]}
              {hoveredArea === 'social' && definitions.social.examples[0]}
              {hoveredArea !== 'legal' && hoveredArea !== 'moral' && hoveredArea !== 'institutional' && hoveredArea !== 'social' && intersections[hoveredArea]?.examples[0]}
            </p>
          </div>
        )}

        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-bold text-lg mb-3">Key Takeaways:</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>• <span className="font-semibold">The Act:</span> Legal definitions focus on what was done (bribery, embezzlement, fraud)</li>
            <li>• <span className="font-semibold">The Intent:</span> Moral frameworks examine the purpose (self-interest vs. public good)</li>
            <li>• <span className="font-semibold">The Context:</span> Institutional analysis considers where it happens (normalized in some spaces)</li>
            <li>• <span className="font-semibold">The Power:</span> Social analysis looks at who does it (class, caste, party affiliation)</li>
            <li>• <span className="font-semibold">The System:</span> "In a capitalist society, corruption is not outside the system. It is part of how capital accumulates, circulates, and escapes control."</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default CorruptionDefinitions;