import React from 'react';
import { Package } from '../../types/api';

interface PackageCardProps {
  package: Package;
  isSelected?: boolean;
  onSelect: () => void;
}

const PackageCard: React.FC<PackageCardProps> = ({
  package: pkg,
  isSelected = false,
  onSelect,
}) => {
  return (
    <div
      className={`relative p-6 rounded-lg border-2 transition-all ${
        isSelected
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-200 hover:border-gray-300'
      }`}
    >
      {isSelected && (
        <div className="absolute top-4 right-4">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            Ausgewählt
          </span>
        </div>
      )}

      <h3 className="text-lg font-medium text-gray-900">{pkg.name}</h3>
      <p className="mt-2 text-sm text-gray-500">{pkg.description}</p>

      <div className="mt-4">
        <span className="text-3xl font-bold text-gray-900">€{pkg.price}</span>
        <span className="text-sm text-gray-500">/Monat</span>
      </div>

      <ul className="mt-6 space-y-4">
        {pkg.features.map((feature, index) => (
          <li key={index} className="flex items-start">
            <svg
              className="flex-shrink-0 h-5 w-5 text-green-500"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
            <span className="ml-2 text-sm text-gray-500">{feature}</span>
          </li>
        ))}
      </ul>

      <button
        onClick={onSelect}
        className={`mt-8 w-full px-4 py-2 rounded-md text-sm font-medium transition-colors ${
          isSelected
            ? 'bg-blue-600 text-white hover:bg-blue-700'
            : 'bg-white text-blue-600 border border-blue-600 hover:bg-blue-50'
        }`}
      >
        {pkg.button_text}
      </button>
    </div>
  );
};

export default PackageCard;
