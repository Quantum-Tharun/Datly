import { Link } from 'react-router-dom';
import { DatlyLogo } from './DatlyLogo';

export function Navbar() {

  return (
    <nav className="w-full flex items-center justify-between py-6 px-6 md:px-12 max-w-7xl mx-auto z-10 relative">
      {/* Logo */}
      <Link to="/" className="flex items-center gap-2 scale-[0.35] origin-left -ml-4 md:ml-0 hover:opacity-80 transition-opacity">
        <DatlyLogo reducedMotion={true} />
      </Link>


    </nav>
  );
}
